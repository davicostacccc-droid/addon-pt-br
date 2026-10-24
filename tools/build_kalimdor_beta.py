"""Compile explicitly experimental regional imports with local, cached narration."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import shutil
import tempfile
import time
import zipfile
from build_pack import digest, generate, key, validate_row

ROOT = Path(__file__).resolve().parents[1]


def safe_lua(value):
    if isinstance(value, bool): return 'true' if value else 'false'
    if isinstance(value, (int, float)): return repr(value)
    # Keep UTF-8 printable text compact; decimal escapes are only for controls.
    return '"' + ''.join('\\'+c if c in '\\"' else f'\\{ord(c):03d}' if ord(c)<32 or ord(c)==127 else c for c in value) + '"'


def narration(text):
    text = re.sub(r'\$[gG]([^:;]*):([^;]*);', lambda m: m[1], text)
    text = re.sub(r'\$[nNcCrR]', 'aventureiro', text)
    # Stage directions stay visible but are omitted from narration.
    text = re.sub(r'<[^<>]*>', '', text)
    return text.strip()


def build(catalog_path, audit_path, out, previous, version='0.4.0-beta1', region='Kalimdor', readme=None):
    if out.exists(): raise FileExistsError('Preserve old releases; choose a new output.')
    data = json.loads(catalog_path.read_text(encoding='utf-8'))
    if data.get('kind') != 'experimental-import-not-manually-reviewed': raise ValueError('Wrong beta catalog')
    audit = json.loads(audit_path.read_text(encoding='utf-8'))
    old_manifest = json.loads((previous / 'manifest.json').read_text(encoding='utf-8'))
    preserved = {r['questID'] for r in old_manifest if 'questID' in r}
    preserved_phases = {(r['questID'],r['event']) for r in old_manifest if 'questID' in r}
    rows = [r for r in data['lines'] if (r['questID'],r['event']) not in preserved_phases]
    model = ROOT / 'models/pt_BR-faber-medium.onnx'
    hashes = digest(model), digest(Path(str(model)+'.json'))
    voices, records, issues = {}, [], list(audit['issues'])
    generated, reused, started = 0, 0, time.monotonic()
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=out.parent) as temp:
        stage = Path(temp) / 'AzerothVoz'
        shutil.copytree(previous, stage)
        for name in ('Core.lua','Events.lua','UI.lua','AzerothVoz.toc'):
            shutil.copyfile(ROOT/'addon/AzerothVoz'/name, stage/name)
        pack = [(stage/'Pack.lua').read_text(encoding='utf-8')]
        manifest = list(old_manifest)
        for i, original in enumerate(rows, 1):
            row = dict(original, spoken=narration(original['translation']))
            validate_row(row)
            try:
                audio, seconds, hit = generate(row, model, *hashes, ROOT/'cache', voices)
            except Exception as error:
                issues.append(dict(quest=row['questID'],phase=row['event'],reason='tts:'+type(error).__name__))
                print(json.dumps(dict(error='tts',quest=row['questID'],event=row['event'],message=str(error)[:160])),flush=True)
                continue
            generated += not hit; reused += hit
            relative = 'audio\\'+audio.name
            if not (stage/'audio'/audio.name).exists(): shutil.copyfile(audio,stage/'audio'/audio.name)
            record = {k:v for k,v in row.items() if k not in ('spoken','translation_source')}
            record.update(audio=relative,duration=seconds)
            pack.append('AzerothVoz.Register({'+','.join(k+'='+safe_lua(v) for k,v in record.items())+'})\n')
            records.append(record)
            manifest.append(dict(key=key(record),questID=row['questID'],event=row['event'],audio=relative,duration=seconds,
                                 sha256=digest(audio),provider='Piper Faber local beta',translation_source=row['translation_source']))
            if i==1 or i%25==0 or i==len(rows):
                print(json.dumps(dict(done=i,total=len(rows),generated=generated,reused=reused,elapsed=round(time.monotonic()-started,1))),flush=True)
        if not records: raise ValueError('No beta records generated.')
        covered = {r['questID'] for r in records} | preserved
        selected = set(audit['selected_ids'])
        previous_coverage = json.loads((previous/'COBERTURA.json').read_text(encoding='utf-8')) if (previous/'COBERTURA.json').exists() else None
        summary = dict(version=version,region=region,selected_quests=len(selected),quests_with_any_phase=len(covered & selected),
                       total_quests_including_preserved=len(covered),quest_phase_records=len(records)+sum('questID' in r for r in old_manifest),
                       imported_records=len(records),generated_audio=generated,reused_audio=reused,
                       quests_without_any_phase=sorted(selected-covered),issues=issues,
                       phases=dict(Counter(r['event'] for r in records)),in_game='PENDING',manual_review='imported text not fully reviewed')
        if previous_coverage:
            (stage/'COBERTURA-ANTERIOR.json').write_text(json.dumps(previous_coverage,ensure_ascii=False,indent=2),encoding='utf-8')
        message=f"Beta {region}: {summary['quests_with_any_phase']} de {len(selected)} IDs regionais com ao menos uma etapa; {len(covered)} IDs no pacote combinado. Cobertura parcial. Consulte COBERTURA.json."
        pack.append('AzerothVoz.packInfo='+safe_lua(message)+'\n')
        (stage/'Pack.lua').write_text(''.join(pack),encoding='utf-8')
        (stage/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
        (stage/'COBERTURA.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
        with (stage/'FONTE-DOS-AUDIOS.txt').open('a',encoding='utf-8') as stream:
            stream.write('\n'+version+': new narration synthesized locally with Piper Faber pt_BR. One standard voice; imported translations are experimental.\n')
        # Copy the final source snapshot after synthesis, allowing UI work to
        # finish while the independent audio batch is running.
        for file in (ROOT/'addon/AzerothVoz').iterdir():
            if file.name!='Pack.lua' and file.suffix in ('.lua','.toc'): shutil.copyfile(file,stage/file.name)
        shutil.copyfile(readme or ROOT/'docs/BETA-KALIMDOR.md',stage/'LEIA-ME.md')
        shutil.copyfile(ROOT/'THIRD_PARTY.md',stage/'THIRD_PARTY.md')
        for file in (previous/'audio').glob('*'):
            if digest(file) != digest(stage/'audio'/file.name): raise ValueError('Previous audio changed')
        stage.replace(out)
    (out.parent/'expected-records.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('issues','quests_without_any_phase')}),flush=True)
    return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog',type=Path,required=True); parser.add_argument('--audit',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True); parser.add_argument('--previous',type=Path,required=True)
    parser.add_argument('--version',default='0.4.0-beta1'); parser.add_argument('--region',default='Kalimdor')
    parser.add_argument('--readme',type=Path)
    args=parser.parse_args(); build(args.catalog,args.audit,args.out,args.previous,args.version,args.region,args.readme)


if __name__=='__main__': main()
