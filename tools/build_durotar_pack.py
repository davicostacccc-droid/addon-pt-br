"""Build a small automatic quest pack from inspected SQL, reviewed text and audio.

Upstream recordings stay in local research/dist only. This does not install WoW.
"""
import array
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile
import imageio_ffmpeg
from build_pack import generate, digest, lua_string, key, validate_row

ROOT = Path(__file__).resolve().parents[1]
EVENTS = {'accept': 'QUEST_DETAIL', 'progress': 'QUEST_PROGRESS', 'complete': 'QUEST_COMPLETE'}


def duration(path):
    data = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-hide_banner', '-loglevel', 'error',
        '-i', str(path), '-f', 's16le', '-acodec', 'pcm_s16le', '-ar', '22050', '-ac', '1', '-'],
        capture_output=True, check=True).stdout
    samples = array.array('h', data)
    if sys.byteorder != 'little': samples.byteswap()
    if not samples or max(abs(x) for x in samples) < 20: raise ValueError('Empty or silent audio.')
    return len(samples) / 22050


def main():
    out = ROOT / 'dist' / 'durotar-0.2.0' / 'AzerothVoz'
    if out.exists(): raise FileExistsError('Choose a new output for an updated build.')
    source = json.loads((ROOT / 'research/azerothcore-english/selected-durotar.json').read_text(encoding='utf-8'))
    reviewed = json.loads((ROOT / 'data/durotar-translations.json').read_text(encoding='utf-8'))
    english = {r['ID']: r for r in source['quest_template']}
    rewards = {r['ID']: r['RewardText'] for r in source['quest_offer_reward']}
    progress = {r['ID']: r['CompletionText'] for r in source['quest_request_items']}
    starters, enders = {}, {}
    for row in source['creature_queststarter']: starters.setdefault(row['quest'], []).append(row['id'])
    for row in source['creature_questender']: enders.setdefault(row['quest'], []).append(row['id'])
    model = ROOT / 'models/pt_BR-faber-medium.onnx'
    hashes = digest(model), digest(Path(str(model) + '.json'))
    cache = ROOT / 'cache'; cache.mkdir(exist_ok=True)
    voices, records, generated = {}, [], 0
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=out.parent) as temp:
        addon = Path(temp) / 'AzerothVoz'
        shutil.copytree(ROOT / 'dist/gornek/AzerothVoz', addon)
        # Update only a generated staging directory, never an installed addon.
        for filename in ('Core.lua', 'Events.lua', 'UI.lua', 'AzerothVoz.toc'):
            shutil.copyfile(ROOT / 'addon/AzerothVoz' / filename, addon / filename)
        lua = (addon / 'Pack.lua').read_text(encoding='utf-8')
        manifest = json.loads((addon / 'manifest.json').read_text(encoding='utf-8'))
        for quest, tr in reviewed['quests'].items():
            quest = int(quest)
            for phase, event in EVENTS.items():
                if phase not in tr: continue
                text = english[quest]['QuestDescription'] if phase == 'accept' else rewards.get(quest) if phase == 'complete' else progress.get(quest)
                if not text: raise ValueError(f'English source missing: {quest}-{phase}')
                npcs = starters.get(quest, []) if phase == 'accept' else enders.get(quest, [])
                if not npcs: raise ValueError(f'NPC relation missing: {quest}-{phase}')
                row = {'event': event, 'npc': npcs[0], 'questID': quest, 'source': text,
                       'translation': tr[phase], 'title': tr['title']}
                if phase == 'accept': row['objectives'] = tr['objectives']
                validate_row(row)
                name = f'{quest}-{phase}'
                original = ROOT / 'research/voiceover-ptbr/audio' / (name + '.mp3')
                provider = 'Darkneo ptBR Vanilla 0.1 — local test'
                if name in reviewed['audio_overrides']:
                    original, _, hit = generate(row, model, *hashes, cache, voices)
                    generated += int(not hit)
                    provider = 'Piper Faber pt_BR — corrected/missing line'
                elif not original.is_file(): raise FileNotFoundError(original)
                relative = 'audio/quest-' + name + '.mp3'
                shutil.copyfile(original, addon / relative)
                seconds = duration(addon / relative)
                for npc in npcs:
                    record = dict(row, npc=npc, audio=relative.replace('/', '\\'), duration=seconds)
                    fields = [f'{field} = ' + (repr(value) if isinstance(value, (int, float)) else lua_string(value))
                              for field, value in record.items()]
                    lua += 'AzerothVoz.Register({ ' + ', '.join(fields) + ' })\n'
                    manifest.append({'key': key(record), 'questID': quest, 'event': event,
                        'audio': record['audio'], 'duration': seconds, 'sha256': digest(addon / relative), 'provider': provider})
                    records.append(record)
        (addon / 'Pack.lua').write_text(lua, encoding='utf-8')
        (addon / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        shutil.copyfile(ROOT / 'docs/TESTE-DUROTAR-0.2.0.md', addon / 'LEIA-ME.md')
        (addon / 'FONTE-DOS-AUDIOS.txt').write_text(
            'Upstream: Darkneo, AI VoiceOver Sounds Vanilla ptBR v0.1, CurseForge file 6516696.\n'
            'https://www.curseforge.com/wow/addons/ai-voiceover-sounds-vanilla-ptbr-lowquality/files/6516696\n'
            'All Rights Reserved. Small local test copy; not published to GitHub.\n'
            'Two missing/conflicting lines use locally synthesized Piper Faber.\n', encoding='utf-8')
        addon.replace(out)
    # Full expected records are local test fixtures, not executed as imported Lua.
    (out.parent / 'expected-records.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'out': str(out), 'quests': len(reviewed['quests']), 'new_records': len(records),
                      'total_records': len(manifest), 'new_syntheses': generated}, ensure_ascii=True))


if __name__ == '__main__': main()
