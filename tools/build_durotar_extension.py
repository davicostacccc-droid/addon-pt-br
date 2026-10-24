"""Build 0.3.0 over the preserved 0.2.1 local audio package; no game writes."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile
import zipfile
from lupa.lua51 import LuaRuntime
from build_pack import digest, generate, key, lua_string, validate_row
from build_durotar_pack import duration
from verify_release import verify

ROOT = Path(__file__).resolve().parents[1]


def extension_records(source, reviewed):
    english = {r['ID']: r for r in source['quest_template']}
    rewards = {r['ID']: r['RewardText'] for r in source['quest_offer_reward']}
    progress = {r['ID']: r['CompletionText'] for r in source['quest_request_items']}
    for quest, tr in reviewed['quests'].items():
        quest = int(quest)
        for phase, event in (('accept', 'QUEST_DETAIL'), ('progress', 'QUEST_PROGRESS'), ('complete', 'QUEST_COMPLETE')):
            text = english[quest]['QuestDescription'] if phase == 'accept' else progress.get(quest) if phase == 'progress' else rewards.get(quest)
            if not text:
                if phase in tr: raise ValueError(f'Translation without source: {quest}-{phase}')
                continue
            relation = 'creature_queststarter' if phase == 'accept' else 'creature_questender'
            npcs = sorted({r['id'] for r in source[relation] if r['quest'] == quest})
            if not npcs: raise ValueError(f'Missing NPC: {quest}-{phase}')
            for npc in npcs:
                row = dict(event=event, npc=npc, questID=quest, source=text, translation=tr[phase], title=tr['title'])
                if phase == 'accept': row['objectives'] = tr['objectives']
                validate_row(row)
                yield phase, row


def main():
    old = ROOT / 'dist/durotar-0.2.1/AzerothVoz'
    parent = ROOT / 'dist/durotar-0.3.0'
    out = parent / 'AzerothVoz'
    zipped = ROOT / 'dist/AzerothVoz-0.3.0-Durotar-12340.zip'
    if out.exists() or zipped.exists(): raise FileExistsError('Preserve existing releases; choose a new version.')
    source = json.loads((ROOT / 'data/durotar-extension-source.json').read_text(encoding='utf-8'))
    reviewed = json.loads((ROOT / 'data/durotar-extension-translations.json').read_text(encoding='utf-8'))
    model = ROOT / 'models/pt_BR-faber-medium.onnx'
    hashes = digest(model), digest(Path(str(model) + '.json'))
    voices, records, generated = {}, [], 0
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=parent) as temp:
        stage = Path(temp) / 'AzerothVoz'
        shutil.copytree(old, stage)
        for name in ('Core.lua', 'UI.lua', 'Events.lua', 'AzerothVoz.toc'):
            shutil.copyfile(ROOT / 'addon/AzerothVoz' / name, stage / name)
        pack = (stage / 'Pack.lua').read_text(encoding='utf-8')
        manifest = json.loads((stage / 'manifest.json').read_text(encoding='utf-8'))
        for phase, row in extension_records(source, reviewed):
            audio, _, hit = generate(row, model, *hashes, ROOT / 'cache', voices)
            generated += not hit
            relative = f"audio/quest-{row['questID']}-{phase}.mp3"
            shutil.copyfile(audio, stage / relative)
            record = dict(row, audio=relative.replace('/', '\\'), duration=duration(stage / relative))
            fields = [f'{k} = ' + (repr(v) if isinstance(v, (int, float)) else lua_string(v)) for k, v in record.items()]
            pack += 'AzerothVoz.Register({ ' + ', '.join(fields) + ' })\n'
            manifest.append(dict(key=key(record), questID=row['questID'], event=row['event'], audio=record['audio'],
                                 duration=record['duration'], sha256=digest(audio), provider='Piper Faber pt_BR local'))
            records.append(record)
        (stage / 'Pack.lua').write_text(pack, encoding='utf-8')
        (stage / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        shutil.copyfile(ROOT / 'docs/TESTE-0.3.0.md', stage / 'LEIA-ME.md')
        with (stage / 'FONTE-DOS-AUDIOS.txt').open('a', encoding='utf-8') as stream:
            stream.write('\n0.3.0: fourteen additional lines synthesized locally using Piper Faber pt_BR.\n')
        for audio in (old / 'audio').glob('*'):
            assert audio.read_bytes() == (stage / 'audio' / audio.name).read_bytes()
        stage.replace(out)
    previous = json.loads((ROOT / 'dist/durotar-0.2.0/expected-records.json').read_text(encoding='utf-8'))
    all_records = previous + records
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute((ROOT / 'tests/wow_stub.lua').read_text(encoding='utf-8'))
    for name in ('Core.lua', 'Pack.lua', 'UI.lua', 'Events.lua'):
        lua.execute((out / name).read_text(encoding='utf-8'))
    lua.execute("Emit('ADDON_LOADED','AzerothVoz'); QuestFrame:Show()")
    for row in all_records:
        lua.globals()._text = re.sub(r'\$([nNcCrRbB])', lambda m: {'n':'Teste','c':'Warrior','r':'Orc','b':'\n'}[m[1].lower()], row['source'])
        lua.globals()._guid = f"0xF130{row['npc']:06X}000001"
        lua.eval('Emit')(row['event']); lua.execute('Tick(0.1)')
        assert lua.eval('AzerothVoz.current.record.questID') == row['questID']
        assert lua.eval('AzerothVoz.current.record.translation') == row['translation']
        lua.execute('assert(not AzerothVoz.reader:IsShown() and AzerothVoz.controls:IsShown())')
        lua.execute("Emit('QUEST_FINISHED')")
    with zipfile.ZipFile(zipped, 'w', zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(out.rglob('*')):
            if file.is_file(): archive.write(file, 'AzerothVoz/' + file.relative_to(out).as_posix())
    report = verify(out, zipped)
    report.update(quest_ui_checks=len(all_records), new_syntheses=generated, previous_audio_preserved=True, in_game='pending')
    (parent / 'expected-records.json').write_text(json.dumps(all_records, ensure_ascii=False, indent=2), encoding='utf-8')
    (parent / 'VERIFICACAO.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    (parent / 'SHA256SUMS.txt').write_text(hashlib.sha256(zipped.read_bytes()).hexdigest() + '  ' + zipped.name + '\n')
    print(json.dumps(dict(zip=str(zipped), records=len(manifest), quest_checks=len(all_records), audio=len(report['unique_audio']), generated=generated)))


if __name__ == '__main__': main()
