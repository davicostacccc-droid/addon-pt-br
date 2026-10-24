"""Package the UI refinement while retaining the already verified 0.2.0 audio."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import zipfile
from lupa.lua51 import LuaRuntime
from verify_release import verify

ROOT = Path(__file__).resolve().parents[1]


def main():
    old = ROOT / 'dist/durotar-0.2.0/AzerothVoz'
    parent = ROOT / 'dist/durotar-0.2.1'
    out = parent / 'AzerothVoz'
    zipped = ROOT / 'dist/AzerothVoz-0.2.1-Durotar-12340.zip'
    if out.exists() or zipped.exists(): raise FileExistsError('Preserve the existing release; use a new output.')
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=parent) as temp:
        stage = Path(temp) / 'AzerothVoz'
        shutil.copytree(old, stage)
        for name in ('Core.lua', 'Events.lua', 'UI.lua', 'AzerothVoz.toc'):
            shutil.copyfile(ROOT / 'addon/AzerothVoz' / name, stage / name)
        (stage / 'docs').mkdir(exist_ok=True)
        shutil.copyfile(ROOT / 'docs/TESTE-DUROTAR-0.2.0.md', stage / 'docs/COBERTURA-0.2.0.md')
        shutil.copyfile(ROOT / 'docs/TESTE-0.2.1.md', stage / 'LEIA-ME.md')
        # The reader/body changes must not change narration content or encoding.
        for file in (old / 'audio').glob('*'):
            if file.read_bytes() != (stage / 'audio' / file.name).read_bytes():
                raise ValueError('Audio changed unexpectedly.')
        stage.replace(out)

    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute((ROOT / 'tests/wow_stub.lua').read_text(encoding='utf-8'))
    for name in ('Core.lua', 'Pack.lua', 'UI.lua', 'Events.lua'):
        lua.execute((out / name).read_text(encoding='utf-8'))
    lua.execute("Emit('ADDON_LOADED','AzerothVoz'); QuestFrame:Show()")
    records = json.loads((old.parent / 'expected-records.json').read_text(encoding='utf-8'))
    checks = []
    for row in records:
        substitutions = {'n': 'Teste', 'c': 'Warrior', 'r': 'Orc', 'b': '\n'}
        text = re.sub(r'\$([nNcCrRbB])', lambda m: substitutions[m[1].lower()], row['source'])
        lua.globals()._text = text
        lua.globals()._guid = f"0xF130{row['npc']:06X}000001"
        lua.eval('Emit')(row['event']); lua.execute('Tick(0.1)')
        assert lua.eval('AzerothVoz.current.record.questID') == row['questID']
        assert lua.eval('AzerothVoz.current.record.translation') == row['translation']
        lua.execute("assert(not AzerothVoz.reader:IsShown() and AzerothVoz.controls:IsShown())")
        lua.execute("assert(QuestInfoObjectivesHeader:GetText() == 'Objetivos')")
        lua.execute("SlashCmdList.AZEROTHVOZ('repetir'); SlashCmdList.AZEROTHVOZ('parar')")
        lua.execute("Emit('QUEST_FINISHED'); assert(not AzerothVoz.controls:IsShown())")
        checks.append({'questID': row['questID'], 'event': row['event']})
    lua.execute("SlashCmdList.AZEROTHVOZ('previa'); assert(AzerothVoz.reader:IsShown())")
    lua.execute("assert(not AzerothVoz.controls:IsShown()); SlashCmdList.AZEROTHVOZ('parar')")
    with zipfile.ZipFile(zipped, 'w', zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(out.rglob('*')):
            if file.is_file(): archive.write(file, 'AzerothVoz/' + file.relative_to(out).as_posix())
    report = verify(out, zipped)
    report['quest_ui_checks'] = checks
    report['audio_unchanged_from_0_2_0'] = True
    (parent / 'VERIFICACAO.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    (parent / 'SHA256SUMS.txt').write_text(hashlib.sha256(zipped.read_bytes()).hexdigest() + '  ' + zipped.name + '\n')
    print(json.dumps({'zip': str(zipped), 'bytes': zipped.stat().st_size, 'quest_ui_checks': len(checks),
        'unique_audio_verified': len(report['unique_audio']), 'zip_verified': report['zip_verified'],
        'in_game': 'pending player confirmation'}, ensure_ascii=True))


if __name__ == '__main__': main()
