"""Verify a generated release using actual Lua 5.1 and MP3 decoding."""
import argparse
import array
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import zipfile
import imageio_ffmpeg
from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]


def verify(addon, zip_path=None):
    manifest = json.loads((addon / 'manifest.json').read_text(encoding='utf-8'))
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute((ROOT / 'tests' / 'wow_stub.lua').read_text(encoding='utf-8'))
    files = [line.strip() for line in (addon / 'AzerothVoz.toc').read_text(encoding='utf-8').splitlines()
             if line.strip() and not line.startswith('#')]
    for name in files:
        lua.execute((addon / name).read_text(encoding='utf-8'))
        if name != 'Pack.lua':
            if (addon / name).read_bytes() != (ROOT / 'addon' / 'AzerothVoz' / name).read_bytes():
                raise ValueError('Código do pacote difere da fonte: ' + name)
    lua.execute("Emit('ADDON_LOADED','AzerothVoz'); SlashCmdList.AZEROTHVOZ('demo'); assert(_music.played == 1)")
    lua.execute("Tick(15); assert(not AzerothVoz.playing and _cv.Sound_MusicVolume == '0.35')")
    catalog = json.loads((ROOT / 'data' / 'demo.json').read_text(encoding='utf-8'))
    row = catalog['lines'][1]
    lua.globals()._text = row['source']
    lua.execute("Emit('GOSSIP_SHOW'); Tick(0.1); assert(_music.played == 2)")
    lua.execute("Emit('GOSSIP_CLOSED'); assert(not AzerothVoz.playing)")
    unique, reports = set(), []
    for row in manifest:
        path = (addon / row['audio'].replace('\\', '/')).resolve()
        if not path.is_relative_to(addon.resolve()):
            raise ValueError('Caminho fora do pacote.')
        if hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
            raise ValueError('Hash de áudio inválido.')
        if path in unique:
            continue
        unique.add(path)
        result = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-hide_banner', '-loglevel', 'error',
            '-i', str(path), '-f', 's16le', '-acodec', 'pcm_s16le', '-ar', '22050', '-ac', '1', '-'],
            capture_output=True, check=True)
        samples = array.array('h', result.stdout)
        if sys.byteorder != 'little':
            samples.byteswap()
        duration = len(samples) / 22050
        rms = math.sqrt(sum(sample * sample for sample in samples) / max(1, len(samples)))
        if rms < 10 or abs(duration - row['duration']) > 0.2:
            raise ValueError('Áudio silencioso ou duração incompatível.')
        reports.append({'audio': path.name, 'seconds': round(duration, 3), 'rms': round(rms, 2)})
    if zip_path:
        with zipfile.ZipFile(zip_path) as zipped:
            if zipped.testzip() is not None:
                raise ValueError('ZIP corrompido.')
            for path in addon.rglob('*'):
                if path.is_file():
                    entry = 'AzerothVoz/' + path.relative_to(addon).as_posix()
                    if zipped.read(entry) != path.read_bytes():
                        raise ValueError('ZIP difere do pacote: ' + entry)
    return {'lua': lua.eval('_VERSION'), 'records': len(manifest), 'unique_audio': reports,
            'zip_verified': bool(zip_path), 'in_game': 'PENDENTE — confirmação do jogador'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('addon', type=Path)
    parser.add_argument('--zip', type=Path)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    result = verify(args.addon, args.zip)
    if args.report:
        args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=True, indent=2))
