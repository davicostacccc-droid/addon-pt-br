"""Build a local audition addon from two supplied patch samples, without installing."""
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
from lupa.lua51 import LuaRuntime
from build_pack import lua_string

ROOT = Path(__file__).resolve().parents[1]


def main():
    folder = ROOT / 'dist' / 'teste-vozes-patch' / 'AzerothVozTeste'
    zip_path = ROOT / 'dist' / 'AzerothVoz-Teste-Jaina-Thrall-12340.zip'
    if folder.exists() or zip_path.exists():
        raise FileExistsError('O teste já foi gerado. Preserve a entrega e use outra saída para atualizá-la.')
    inputs = [('jaina', 'jaina.wav', 'Jaina — saudação'),
              ('thrall', 'thrall-greeting02.wav', 'Thrall — saudação')]
    for _, name, _ in inputs:
        if not (ROOT / 'research' / 'patch-audio' / name).is_file():
            raise FileNotFoundError('Extraia primeiro a amostra local: ' + name)
    folder.parent.mkdir(parents=True, exist_ok=True)
    reports = []
    with tempfile.TemporaryDirectory(dir=folder.parent) as temp:
        addon = Path(temp) / 'AzerothVozTeste'
        shutil.copytree(ROOT / 'experiments' / 'AzerothVozTeste', addon)
        (addon / 'audio').mkdir()
        table = ['AzerothVozTesteSamples = {']
        for name, filename, label in inputs:
            source = ROOT / 'research' / 'patch-audio' / filename
            target = addon / 'audio' / (name + '.mp3')
            subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-hide_banner', '-loglevel', 'error',
                '-i', str(source), '-ac', '1', '-codec:a', 'libmp3lame', '-b:a', '96k', str(target)],
                capture_output=True, check=True)
            decoded = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-hide_banner', '-loglevel', 'error',
                '-i', str(target), '-f', 's16le', '-acodec', 'pcm_s16le', '-ar', '22050', '-ac', '1', '-'],
                capture_output=True, check=True).stdout
            samples = array.array('h', decoded)
            if sys.byteorder != 'little': samples.byteswap()
            if not samples or max(abs(x) for x in samples) < 20:
                raise ValueError('Áudio vazio ou silencioso: ' + name)
            duration = len(samples) / 22050
            table.append(f'  {name} = {{ label = {lua_string(label)}, duration = {duration!r} }},')
            reports.append({'sample': name, 'duration': duration,
                'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                'mp3_sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
        table.append('}')
        (addon / 'Samples.lua').write_text('\n'.join(table) + '\n', encoding='utf-8')
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute((ROOT / 'tests' / 'wow_stub.lua').read_text(encoding='utf-8'))
        for file in ('Samples.lua', 'Core.lua'):
            lua.execute((addon / file).read_text(encoding='utf-8'))
        lua.execute("Emit('ADDON_LOADED','AzerothVozTeste'); SlashCmdList.AZEROTHVOZTESTE('jaina'); assert(_music.played == 1)")
        lua.execute("SlashCmdList.AZEROTHVOZTESTE('volume 40'); assert(_cv.Sound_MusicVolume == '0.4')")
        lua.execute("SlashCmdList.AZEROTHVOZTESTE('thrall'); assert(_music.played == 2 and _music.stopped == 1)")
        lua.execute("Tick(20); assert(_cv.Sound_MusicVolume == '0.35' and _cv.Sound_EnableMusic == '0')")
        lua.execute("SlashCmdList.AZEROTHVOZTESTE('jaina'); SlashCmdList.AZEROTHVOZTESTE('parar'); assert(_cv.Sound_MusicVolume == '0.35')")
        lua.execute("SlashCmdList.AZEROTHVOZTESTE('thrall'); Emit('PLAYER_LOGOUT'); assert(_cv.Sound_MusicVolume == '0.35')")
        report = {'samples': reports, 'lua': 'Lua 5.1', 'commands_and_volume_simulation': 'passed',
                  'in_game': 'pending player confirmation', 'installed_in_wow': False}
        (addon / 'VERIFICACAO.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
        addon.replace(folder)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipped:
        for file in sorted(folder.rglob('*')):
            if file.is_file(): zipped.write(file, 'AzerothVozTeste/' + file.relative_to(folder).as_posix())
    with zipfile.ZipFile(zip_path) as zipped:
        assert zipped.testzip() is None
        for file in folder.rglob('*'):
            if file.is_file(): assert zipped.read('AzerothVozTeste/' + file.relative_to(folder).as_posix()) == file.read_bytes()
    (folder.parent / 'SHA256SUMS.txt').write_text(hashlib.sha256(zip_path.read_bytes()).hexdigest() + '  ' + zip_path.name + '\n')
    print(json.dumps(dict(report, zip=str(zip_path), bytes=zip_path.stat().st_size), ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
