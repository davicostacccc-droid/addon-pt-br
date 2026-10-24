"""Verify the large beta before creating its installable ZIP."""
import argparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import json
import math
from pathlib import Path
import re
import subprocess
import time
import zipfile
import imageio_ffmpeg
from lupa.lua51 import LuaRuntime
from build_pack import digest
from import_quest_locale_sql import read_rows

ROOT = Path(__file__).resolve().parents[1]


def decode_audio(item):
    path, expected = item
    result = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-nostats','-i',str(path),
                             '-af','volumedetect','-f','null','-'],capture_output=True,check=True)
    log = result.stderr.decode('utf-8',errors='replace')
    duration = re.search(r'Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)',log)
    volume = re.search(r'mean_volume:\s*(-?\d+(?:\.\d+)?) dB',log)
    if not duration or not volume: raise ValueError('Missing decoded audio metadata: '+path.name)
    seconds = int(duration[1])*3600+int(duration[2])*60+float(duration[3])
    db = float(volume[1])
    if seconds<=0 or abs(seconds-expected)>.2 or db < -70: raise ValueError('Invalid/silent audio: '+path.name)
    return dict(audio=path.name,seconds=seconds,mean_db=db)


def verify(out, zipped, preserved_paths=None, regional_audit=None, roleplay_checks=False):
    if zipped.exists(): raise FileExistsError('Preserve existing ZIPs')
    started = time.monotonic()
    manifest=json.loads((out/'manifest.json').read_text(encoding='utf-8'))
    imported=json.loads((out.parent/'expected-records.json').read_text(encoding='utf-8'))
    preserved=[]
    for path in preserved_paths or [ROOT/'dist/durotar-0.3.0/expected-records.json']:
        preserved.extend(json.loads(path.read_text(encoding='utf-8')))
    coverage=json.loads((out/'COBERTURA.json').read_text(encoding='utf-8'))
    available=defaultdict(set)
    for row in preserved+imported: available[row['questID']].add(row['event'])
    # Report completion against actual nonempty dialogue phases in the English
    # snapshot, not an assumption that every quest has exactly three phases.
    expected=defaultdict(set)
    selected=set(json.loads(regional_audit.read_text(encoding='utf-8'))['selected_ids']) if regional_audit else set(available) | set(coverage['quests_without_any_phase'])
    combined_selected=set(selected) | set(available)
    previous_coverage=out/'COBERTURA-ANTERIOR.json'
    if previous_coverage.exists():
        previous=json.loads(previous_coverage.read_text(encoding='utf-8'))
        combined_selected.update(previous.get('selected_ids',previous.get('quests_without_any_phase',[])))
    for name,event,field in [('quest_template','QUEST_DETAIL','QuestDescription'),
                             ('quest_request_items','QUEST_PROGRESS','CompletionText'),
                             ('quest_offer_reward','QUEST_COMPLETE','RewardText')]:
        sql=ROOT/'research/azerothcore-english'/(name+'.sql')
        for row in read_rows(sql.read_text(encoding='utf-8-sig'),name):
            if row['ID'] in combined_selected and row[field]: expected[row['ID']].add(event)
    coverage['quests_with_all_reference_phases']=sum(bool(expected.get(q)) and expected[q]<=available.get(q,set()) for q in selected)
    coverage['selected_ids']=sorted(selected)
    coverage['combined_selected_quests']=len(combined_selected)
    coverage['combined_quests_with_all_reference_phases']=sum(bool(expected.get(q)) and expected[q]<=available.get(q,set()) for q in combined_selected)
    coverage['combined_quests_without_any_phase']=sorted(combined_selected-set(available))
    coverage['distinct_quest_phases']=sum(len(es) for es in available.values())
    coverage['manual_review']='Imported text NOT fully manually reviewed; all-reference-phases means coverage, not certified accuracy.'
    (out/'COBERTURA.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2),encoding='utf-8')
    references = []
    for path,url in [
        (ROOT/'research/questtradutor/QuestData_BR.lua','https://github.com/leoaviana/questtradutor/blob/master/QuestData_BR.lua'),
        (ROOT/'research/acstruclocdump-ptbr.sql','https://gist.github.com/heyitsbench/ab41711d41c6eb137d053100c51841da'),
        (ROOT/'models/pt_BR-faber-medium.onnx','https://huggingface.co/rhasspy/piper-voices/tree/main/pt/pt_BR/faber/medium')]:
        references.append(dict(file=path.name,url=url,sha256=digest(path)))
    for table in ('quest_template','quest_request_items','quest_offer_reward','creature_queststarter','creature_questender'):
        path=ROOT/'research/azerothcore-english'/(table+'.sql')
        references.append(dict(file=path.name,url='https://github.com/azerothcore/azerothcore-wotlk/blob/master/data/sql/base/db_world/'+path.name,sha256=digest(path)))
    (out/'PROVENIENCIA.json').write_text(json.dumps(dict(target_build=12340,date='2026-10-24',references=references),indent=2),encoding='utf-8')
    lua=LuaRuntime(unpack_returned_tuples=True)
    lua.execute((ROOT/'tests/wow_stub.lua').read_text(encoding='utf-8'))
    lua.execute('AzerothVozDB={roleplay=false}')
    load_start=time.monotonic()
    toc=(out/'AzerothVoz.toc').read_text(encoding='utf-8')
    for name in [s.strip() for s in toc.splitlines() if s.strip() and not s.startswith('#')]:
        lua.execute((out/name).read_text(encoding='utf-8'))
        if name!='Pack.lua' and (out/name).read_bytes()!=(ROOT/'addon/AzerothVoz'/name).read_bytes():
            raise ValueError('Release code differs from source: '+name)
    load_seconds=time.monotonic()-load_start
    lua.execute("Emit('ADDON_LOADED','AzerothVoz'); QuestFrame:Show(); function GetTitleText() return _title end")
    checks=0; mismatches=[]
    for sex in (2,3):
        lua.globals()._testSex=sex
        lua.execute('UnitSex=function() return _testSex end')
        for row in preserved+imported:
            lua.globals()._text=lua.eval('AzerothVoz.ResolveSource')(row['source'])
            lua.globals()._title=row.get('sourceTitle','English title')
            lua.globals()._guid=f"0xF130{row['npc']:06X}000001" if row['npc'] else None
            lua.eval('Emit')(row['event']); lua.execute('Tick(0.1)')
            q=lua.eval('AzerothVoz.current and AzerothVoz.current.record and AzerothVoz.current.record.questID')
            if q!=row['questID']:
                mismatches.append(dict(quest=row['questID'],event=row['event'],npc=row['npc'],sex=sex,selected=q))
            else:
                assert lua.eval('AzerothVoz.current.record.translation')==row['translation']
                lua.execute('assert(AzerothVoz.playing and not AzerothVoz.reader:IsShown() and AzerothVoz.controls:IsShown())')
                checks+=1
            lua.execute("Emit('QUEST_FINISHED'); assert(not AzerothVoz.playing and not AzerothVoz.controls:IsShown())")
    if mismatches:
        (out.parent/'FAILED-LOOKUPS.json').write_text(json.dumps(mismatches,indent=2),encoding='utf-8')
        raise ValueError(f'{len(mismatches)} ambiguous/missing runtime records; inspect FAILED-LOOKUPS.json')
    rp_checks=0
    if roleplay_checks:
        lua.execute('AzerothVozDB.roleplay=true')
        samples=(preserved+imported)[::max(1,len(preserved+imported)//100)]
        for row in samples:
            lua.globals()._text=lua.eval('AzerothVoz.ResolveSource')(row['source'])
            lua.globals()._title=row.get('sourceTitle','English title')
            lua.globals()._guid=f"0xF130{row['npc']:06X}000001" if row['npc'] else None
            lua.eval('Emit')(row['event']); lua.execute('Tick(0.1); Tick(0.1)')
            lua.execute('assert(AzerothVoz.roleplay:IsShown() and not AzerothVoz.reader:IsShown() and not AzerothVoz.controls:IsShown())')
            assert lua.eval('AzerothVoz.roleplay.modelReady') == bool(row['npc'])
            lua.execute("Emit('QUEST_FINISHED'); assert(not AzerothVoz.roleplay:IsShown() and not AzerothVoz.roleplay.shade:IsShown())")
            rp_checks+=1
        lua.execute("SlashCmdList.AZEROTHVOZ('rp off')")
    lua.execute("SlashCmdList.AZEROTHVOZ('demo'); assert(AzerothVoz.playing); SlashCmdList.AZEROTHVOZ('parar')")
    unique={}
    for row in manifest:
        path=(out/row['audio'].replace('\\','/')).resolve()
        if not path.is_relative_to(out.resolve()): raise ValueError('Audio outside package')
        if digest(path)!=row['sha256']: raise ValueError('Audio hash mismatch')
        if not math.isfinite(row['duration']) or row['duration']<=0: raise ValueError('Invalid duration')
        if path in unique and abs(unique[path]-row['duration'])>.01: raise ValueError('Conflicting audio durations')
        unique[path]=row['duration']
    print(json.dumps(dict(lua_checks=checks,load_seconds=round(load_seconds,3),unique_audio=len(unique))),flush=True)
    reports=[]
    with ThreadPoolExecutor(max_workers=2) as pool:
        for i, report in enumerate(pool.map(decode_audio,unique.items()),1):
            reports.append(report)
            if i%100==0: print(json.dumps(dict(audio_decoded=i,total=len(unique))),flush=True)
    with zipfile.ZipFile(zipped,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for file in sorted(out.rglob('*')):
            if file.is_file(): archive.write(file,'AzerothVoz/'+file.relative_to(out).as_posix())
    with zipfile.ZipFile(zipped) as archive:
        if archive.testzip() is not None: raise ValueError('Corrupted ZIP')
        for file in out.rglob('*'):
            if file.is_file() and archive.read('AzerothVoz/'+file.relative_to(out).as_posix())!=file.read_bytes():
                raise ValueError('ZIP byte mismatch')
    report=dict(lua='Lua 5.1',quest_event_checks=checks,roleplay_event_checks=rp_checks,load_seconds=load_seconds,unique_audio=reports,
                zip_verified=True,zip_sha256=digest(zipped),elapsed_seconds=time.monotonic()-started,in_game='pending player confirmation')
    (out.parent/'VERIFICACAO.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    (out.parent/'SHA256SUMS.txt').write_text(digest(zipped)+'  '+zipped.name+'\n')
    print(json.dumps(dict(zip=str(zipped),bytes=zipped.stat().st_size,checks=checks,audio=len(unique),verified=True)),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('addon',type=Path);parser.add_argument('--zip',type=Path,required=True)
    parser.add_argument('--preserved-records',type=Path,action='append')
    parser.add_argument('--regional-audit',type=Path);parser.add_argument('--roleplay',action='store_true')
    args=parser.parse_args();verify(args.addon,args.zip,args.preserved_records,args.regional_audit,args.roleplay)
