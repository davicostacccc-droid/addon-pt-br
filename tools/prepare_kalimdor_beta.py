"""Prepare a local beta catalog, keeping imported translations explicitly unreviewed.

Reads reference files as data only. Full external catalogs stay outside Git.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
from build_pack import normalize
from import_quest_locale_sql import read_rows
from read_lua_data import numeric_rows

# Original 3.3.5 AreaTable IDs: surface zones, capitals, starting subzones,
# Azuremyst/Bloodmyst/Exodar, and Kalimdor instances. No Cataclysm zone IDs.
ZONES = {14,15,16,17,141,148,215,331,357,361,400,405,406,440,490,493,618,
         1377,1637,1638,1657,3524,3525,3557,363,220,221,188,2577,718,719,
         491,722,1176,2100,2159,2437,2557,3428,3429}
ENGLISH = {'the','you','your','and','of','to','with','have','will','for','that','this','from','are','not','has','was','our','they','them'}
WORDS = {'zero':0,'one':1,'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,'eight':8,'nine':9,'ten':10,
         'eleven':11,'twelve':12,'thirteen':13,'fourteen':14,'fifteen':15,'sixteen':16,'seventeen':17,'eighteen':18,
         'nineteen':19,'twenty':20,'thirty':30,'forty':40,'fifty':50,'hundred':100,
         'um':1,'uma':1,'dois':2,'duas':2,'três':3,'quatro':4,'cinco':5,'seis':6,'sete':7,'oito':8,'nove':9,'dez':10,
         'onze':11,'doze':12,'treze':13,'catorze':14,'quatorze':14,'quinze':15,'dezesseis':16,'dezessete':17,
         'dezoito':18,'dezenove':19,'vinte':20,'trinta':30,'quarenta':40,'cinquenta':50,'cem':100}


def convert(text):
    text = (text or '').replace('NEW_LINE', '\n').replace('YOUR_NAME', '$n')
    text = re.sub(r'YOUR_GENDER\(([^;()]*);([^()]*)\)', lambda m: '$g'+m[1]+':'+m[2]+';', text)
    text = re.sub(r'YOUR_CLASS[1-7]?', '$c', text)
    text = re.sub(r'YOUR_RACE[1-7]?', '$r', text)
    text = re.sub(r'\$[bB]', '\n', text)
    return text.strip()


def numbers(text):
    # Numbers are a conservative warning filter, not a proof of semantic equality.
    tokens = re.findall(r'\d+|[^\W\d_]+', text.lower(), re.UNICODE)
    return {int(w) if w.isascii() and w.isdigit() else WORDS[w] for w in tokens if w.isascii() and w.isdigit() or w in WORDS and WORDS[w] >= 2}


def acceptable(text, english):
    if not text: return 'empty'
    if normalize(text) == normalize(english): return 'english_copy'
    words = re.findall(r'[^\W\d_]+', text.lower(), re.UNICODE)
    en = sum(w in ENGLISH for w in words)
    if en >= 3 and en / max(1, len(words)) > .16: return 'likely_english'
    if re.search(r'(?:YOUR|NPC)_[A-Z]|NEW_LINE|\|[A-Za-z]|\[\[', text): return 'unsupported_markup'
    markers = re.sub(r'\$[gG][^:;]*:[^;]*;', '', text)
    markers = re.sub(r'\$[nNcCrR]', '', markers)
    if '$' in markers: return 'unsupported_marker'
    if numbers(text) != numbers(english): return 'number_difference'
    return None


def source_supported(text):
    text = re.sub(r'\$[gG][^:;]*:[^;]*;', '', text)
    return '$' not in re.sub(r'\$[nNcCrRbB]', '', text)


def prepare(research, questie):
    base = research / 'azerothcore-english'
    def table(name): return list(read_rows((base / (name + '.sql')).read_text(encoding='utf-8-sig'), name))
    english = {r['ID']: r for r in table('quest_template')}
    starters, enders = {}, {}
    for r in table('creature_queststarter'): starters.setdefault(r['quest'], set()).add(r['id'])
    for r in table('creature_questender'): enders.setdefault(r['quest'], set()).add(r['id'])
    selected = {q for q, r in english.items() if r['QuestSortID'] in ZONES}
    possible = {npc for q, ns in starters.items() if english.get(q, {}).get('QuestSortID', 0) < 0 for npc in ns}
    npcs = dict(numeric_rows((questie / 'Database/Wotlk/wotlkNpcDB.lua').read_text(encoding='utf-8-sig'), only=possible))
    related = {q for q, ns in starters.items() if english.get(q, {}).get('QuestSortID', 0) < 0 and any(
        n in npcs and (set((npcs[n].get(7) or {}).keys()) & ZONES or npcs[n].get(9) in ZONES) for n in ns)}
    selected |= related
    rewards = {r['ID']: r['RewardText'] for r in table('quest_offer_reward')}
    progress = {r['ID']: r['CompletionText'] for r in table('quest_request_items')}
    qtr = dict(numeric_rows((research / 'questtradutor/QuestData_BR.lua').read_text(encoding='utf-8-sig'), quoted=True))
    locale = json.loads((research / 'ptbr-staging/quest-translations.json').read_text(encoding='utf-8'))['quests']
    lines, issues, stats = [], [], Counter()
    for q in sorted(selected):
        en = english[q]; tr = locale.get(str(q), {}); old = qtr.get(q, {})
        title = convert(tr.get('Title') or old.get('Title') or en['LogTitle'])
        objectives = None
        for candidate in (tr.get('Objectives'), old.get('Objectives')):
            candidate = convert(candidate)
            if not acceptable(candidate, en['LogDescription'] or ''):
                objectives = candidate; break
        for phase, event, source, fields, speakers in (
            ('accept','QUEST_DETAIL',en['QuestDescription'],[(tr.get('Details'),'locale'),(old.get('Description'),'qtr')],starters.get(q)),
            ('progress','QUEST_PROGRESS',progress.get(q),[(old.get('Progress'),'qtr')],enders.get(q)),
            ('complete','QUEST_COMPLETE',rewards.get(q),[(old.get('Completion'),'qtr')],enders.get(q))):
            if not source: continue
            if not source_supported(source): issues.append(dict(quest=q,phase=phase,reason='source_marker')); continue
            translation, provider, rejected = None, None, []
            for candidate, origin in fields:
                candidate = convert(candidate)
                reason = acceptable(candidate, source)
                if not reason: translation, provider = candidate, origin; break
                rejected.append(origin+':'+reason)
            if not translation:
                issues.append(dict(quest=q,phase=phase,reason=','.join(rejected))); continue
            # NPC zero is strictly an unbound, exact-text fallback for item/object
            # windows. Runtime refuses ambiguous matches; no imagined object GUID.
            for npc in sorted(speakers or {0}):
                row = dict(event=event,npc=npc,questID=q,source=source,translation=translation,title=title,sourceTitle=en['LogTitle'],
                           beta_import=True,translation_source=provider)
                if phase == 'accept' and objectives: row['objectives'] = objectives
                lines.append(row)
            stats[provider+':'+phase] += 1
    # Identical source/title/speaker combinations can belong to mutually exclusive
    # class/race/era quests. Do not arbitrarily choose one imported translation.
    groups = defaultdict(list)
    for row in lines:
        identity = (row['event'],row['npc'],normalize(re.sub(r'\$[bB]', '\n', row['source'])),normalize(row['sourceTitle']))
        groups[identity].append(row)
    ambiguous = {id(row) for group in groups.values() if len({r['questID'] for r in group}) > 1 for row in group}
    for row in lines:
        if id(row) in ambiguous: issues.append(dict(quest=row['questID'],phase=row['event'],reason='ambiguous_source_and_title'))
    lines = [row for row in lines if id(row) not in ambiguous]
    stats = Counter(provider+':'+{'QUEST_DETAIL':'accept','QUEST_PROGRESS':'progress','QUEST_COMPLETE':'complete'}[event]
                    for provider,event,q in {(r['translation_source'],r['event'],r['questID']) for r in lines})
    return dict(version=1,kind='experimental-import-not-manually-reviewed',lines=lines), dict(
        selection=len(selected),zone_ids=sorted(ZONES),related_quests=len(related),imported_quests=len({r['questID'] for r in lines}),
        records=len(lines),phases=dict(stats),issues=issues,selected_ids=sorted(selected))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--research',type=Path,required=True); parser.add_argument('--questie',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    if args.out.exists(): raise FileExistsError('Choose a new output directory')
    catalog,audit=prepare(args.research,args.questie)
    args.out.mkdir(parents=True)
    for name,data in [('catalog.json',catalog),('audit.json',audit)]:
        (args.out/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in audit.items() if k not in ('issues','selected_ids','zone_ids')}))


if __name__ == '__main__': main()
