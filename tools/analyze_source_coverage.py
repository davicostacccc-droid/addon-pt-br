"""Compare local source IDs without executing third-party Lua or SQL.

Only metadata/counts are exported. This does not certify translations, voices,
licensing, server compatibility or the contents of any web database.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re

from import_quest_locale_sql import read_rows


def literal_ids(path):
    # Questie files have one numeric record key at the start of each data line.
    # Do not execute their loader or nested Lua expressions.
    return {int(x) for x in re.findall(r'^\[(\d+)\]\s*=', Path(path).read_text(encoding='utf-8-sig'), re.M)}


def audio_phases(entries):
    result = {}
    for entry in entries:
        match = re.search(r'/sounds/quests/(\d+)-(accept|progress|complete)\.mp3$', entry['path'])
        if match:
            result.setdefault(int(match[1]), set()).add(match[2])
    return result


def summarize(english, localized, questie, questie_pt, audio):
    english_ids = set(english)
    translated = {int(k) for k, row in localized.items() if isinstance(row.get('Details'), str) and row['Details'].strip()}
    intersection = english_ids & translated & questie
    candidates = intersection & set(audio)
    return {
        'english_quest_records': len(english_ids),
        'locale_records': len(localized),
        'locale_nonempty_details': len(translated),
        'questie_quest_ids': len(questie),
        'questie_ptbr_ids': len(questie_pt),
        'questie_ptbr_overlap': len(questie & questie_pt),
        'audio_quest_ids': len(audio),
        'audio_phase_counts': dict(Counter(phase for phases in audio.values() for phase in phases)),
        'english_with_locale_details_and_questie_id': len(intersection),
        'also_has_any_indexed_audio': len(candidates),
        'also_has_all_three_audio_phases': sum(audio[q] >= {'accept', 'progress', 'complete'} for q in candidates),
        'warning': 'ID intersection only: text, language, counts, NPC, phase, audio wording and reuse terms still require review.'
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--research', type=Path, required=True)
    parser.add_argument('--questie', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists(): raise FileExistsError('Preserve existing reports; choose a new output.')
    sql = args.research / 'azerothcore-english/quest_template.sql'
    english = {r['ID']: r for r in read_rows(sql.read_text(encoding='utf-8-sig'), 'quest_template')}
    localized = json.loads((args.research / 'ptbr-staging/quest-translations.json').read_text(encoding='utf-8'))['quests']
    quests = literal_ids(args.questie / 'Database/Wotlk/wotlkQuestDB.lua')
    pt = literal_ids(args.questie / 'Localization/lookups/Wotlk/lookupQuests/ptBR.lua')
    audio = audio_phases(json.loads((args.research / 'voiceover-ptbr/zip-index.json').read_text(encoding='utf-8')))
    report = {'kind': 'reference-coverage-not-playable', 'summary': summarize(english, localized, quests, pt, audio)}
    report['valley_of_trials_reference_ids'] = sorted(q for q, r in english.items() if r['QuestSortID'] == 363)
    # IDs only: no full external text or audio is copied into the report.
    report['valley_of_trials'] = [dict(quest_id=q, questie=q in quests, locale_details=bool(localized.get(str(q), {}).get('Details')),
                                      audio_phases=sorted(audio.get(q, set()))) for q in report['valley_of_trials_reference_ids']]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps(report['summary'], ensure_ascii=True))


if __name__ == '__main__': main()
