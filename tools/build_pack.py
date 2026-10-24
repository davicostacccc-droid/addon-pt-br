"""Offline package compiler. JSON is data; never execute captured Lua."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import wave

ROOT = Path(__file__).resolve().parents[1]
EVENTS = {'DEMO', 'QUEST_DETAIL', 'QUEST_PROGRESS', 'QUEST_COMPLETE', 'GOSSIP_SHOW', 'QUEST_GREETING'}
ASCII_LOWER = str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')


def normalize(text):
    # Exactly Lua 5.1 byte lower + ASCII whitespace (not Unicode str.lower).
    return re.sub(r'[ \t\r\n\v\f]+', ' ', text.translate(ASCII_LOWER)).strip(' ')


def text_hash(text):
    value = 5381
    for byte in text.encode('utf-8'):
        value = (value * 33 + byte) % 2147483647
    return str(value)


def key(row):
    return f"{row['event']}:{row['npc']}:{text_hash(normalize(row['source']))}"


def lua_string(text):
    # ASCII decimal escapes avoid quoting, code injection and UTF-8 ambiguity.
    return '"' + ''.join(f'\\{byte:03d}' for byte in text.encode('utf-8')) + '"'


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def validate_row(row, translated=True):
    if not isinstance(row, dict) or row.get('event') not in EVENTS:
        raise ValueError('Evento inválido no catálogo.')
    if type(row.get('npc')) is not int or not 0 <= row['npc'] <= 0xFFFFFF:
        raise ValueError('NPC deve ser um ID inteiro entre 0 e 16777215.')
    for field in ('source', 'translation') if translated else ('source',):
        if not isinstance(row.get(field), str) or not row[field].strip() or len(row[field]) > 30000:
            raise ValueError(f'Campo {field} vazio, inválido ou muito longo.')
    for field in ('title', 'objectives', 'spoken'):
        if field in row and (not isinstance(row[field], str) or len(row[field]) > 30000):
            raise ValueError(f'Campo {field} inválido.')
    if translated:
        if row.get('review_required'):
            raise ValueError('Revise a tradução automática e remova review_required antes de gerar o pacote.')
        spoken_text(row)  # Validate narration before loading models.


def spoken_text(row):
    # Generic voiced address avoids generating an audio for every player name.
    text = row.get('spoken') or row['translation']
    text = re.sub(r'\$[nN]', 'aventureiro', text)
    if re.search(r'\$[A-Za-z]|\|[A-Za-z]|\[\[', text):
        raise ValueError('Resolva marcadores do jogo/fonemas antes de gerar a voz.')
    return text


def load_catalog(path):
    data = json.loads(Path(path).read_text(encoding='utf-8-sig'))
    if data.get('version') != 1 or not isinstance(data.get('lines'), list):
        raise ValueError('Esperado catálogo JSON versão 1 com lines[].')
    seen = set()
    for row in data['lines']:
        validate_row(row)
        identity = row['event'], row['npc'], normalize(row['source'])
        if identity in seen:
            raise ValueError('Fala duplicada no catálogo.')
        seen.add(identity)
    return data


def valid_cache(audio, metadata, fingerprint):
    try:
        meta = json.loads(metadata.read_text(encoding='utf-8'))
        duration = meta['duration']
        if (meta['fingerprint'] == fingerprint and meta['sha256'] == digest(audio)
                and isinstance(duration, (float, int)) and math.isfinite(duration) and duration > 0):
            return meta
    except (OSError, ValueError, KeyError):
        pass
    return None


def generate(row, voice, model_sha, config_sha, cache, voices):
    from piper import PiperVoice
    import imageio_ffmpeg
    spec = {'text': spoken_text(row), 'model_sha256': model_sha,
            'config_sha256': config_sha, 'engine': importlib.metadata.version('piper-tts'),
            'encoding': 'mp3-libmp3lame-64k-v1'}
    fingerprint = hashlib.sha256(json.dumps(spec, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    audio, metadata = cache / f'{fingerprint}.mp3', cache / f'{fingerprint}.json'
    cached = valid_cache(audio, metadata, fingerprint)
    if cached:
        return audio, cached['duration'], True
    voice_key = str(voice.resolve())
    if voice_key not in voices:
        voices[voice_key] = PiperVoice.load(str(voice))
    with tempfile.TemporaryDirectory(dir=cache) as temp:
        wav_path = Path(temp) / 'speech.wav'
        with wave.open(str(wav_path), 'wb') as output:
            voices[voice_key].synthesize_wav(spec['text'], output)
        with wave.open(str(wav_path), 'rb') as wav:
            duration = wav.getnframes() / wav.getframerate()
            if duration <= 0:
                raise ValueError('Piper gerou áudio vazio.')
        mp3_path = Path(temp) / 'speech.mp3'
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-hide_banner', '-loglevel', 'error',
                        '-i', str(wav_path), '-ac', '1', '-codec:a', 'libmp3lame', '-b:a', '64k',
                        str(mp3_path)], check=True, capture_output=True)
        mp3_path.replace(audio)
    meta = {'fingerprint': fingerprint, 'duration': duration, 'sha256': digest(audio), 'spec': spec}
    metadata.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
    return audio, duration, False


def build(catalog, model, out, cache, voice_map=None):
    data = load_catalog(catalog)
    if out.exists():
        raise FileExistsError(f'A saída já existe; escolha outra pasta: {out}')
    voice_map = voice_map or {}
    # Resolve every voice before producing output; no guessing race/personality.
    selected = {}
    for row in data['lines']:
        voice = Path(voice_map.get(str(row['npc']), model)).resolve()
        config = Path(str(voice) + '.json')
        selected[str(voice)] = (voice, digest(voice), digest(config))
    cache.mkdir(parents=True, exist_ok=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    generated, reused, voices, manifest = 0, 0, {}, []
    # Build in staging and move only a complete addon into its final directory.
    with tempfile.TemporaryDirectory(dir=out.parent) as staging:
        addon = Path(staging) / 'AzerothVoz'
        shutil.copytree(ROOT / 'addon' / 'AzerothVoz', addon)
        (addon / 'audio').mkdir()
        lua = ['-- Generated from a reviewed JSON catalog. No executable capture imports.']
        for row in data['lines']:
            voice = Path(voice_map.get(str(row['npc']), model)).resolve()
            audio, duration, hit = generate(row, *selected[str(voice)], cache, voices)
            reused += int(hit)
            generated += int(not hit)
            relative = f'audio\\{audio.name}'
            shutil.copyfile(audio, addon / 'audio' / audio.name)
            record = dict(row, audio=relative, duration=duration)
            fields = []
            for field in ('event', 'npc', 'source', 'translation', 'title', 'objectives', 'audio', 'duration'):
                if field in record:
                    value = record[field]
                    literal = repr(value) if isinstance(value, (float, int)) else lua_string(value)
                    fields.append(f'{field} = {literal}')
            lua.append('AzerothVoz.Register({ ' + ', '.join(fields) + ' })')
            manifest.append({'key': key(row), 'audio': relative, 'duration': duration,
                             'sha256': digest(audio), 'voice': voice.name})
        (addon / 'Pack.lua').write_text('\n'.join(lua) + '\n', encoding='utf-8')
        (addon / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
        shutil.copyfile(ROOT / 'THIRD_PARTY.md', addon / 'THIRD_PARTY.md')
        shutil.copyfile(ROOT / 'README.md', addon / 'LEIA-ME.md')
        addon.replace(out)
    return {'generated': generated, 'reused': reused, 'lines': len(manifest), 'out': str(out)}


def main():
    parser = argparse.ArgumentParser(description='Gera um pacote PT-BR offline com Piper e cache.')
    parser.add_argument('--catalog', type=Path, default=ROOT / 'data' / 'demo.json')
    parser.add_argument('--model', type=Path, default=ROOT / 'models' / 'pt_BR-faber-medium.onnx')
    parser.add_argument('--out', type=Path, required=True, help='Nova pasta final chamada AzerothVoz')
    parser.add_argument('--cache', type=Path, default=ROOT / 'cache')
    parser.add_argument('--voice-map', type=Path, help='JSON: ID do NPC -> caminho do modelo ONNX')
    args = parser.parse_args()
    if args.out.name != 'AzerothVoz':
        parser.error('--out deve terminar com a pasta AzerothVoz.')
    mapping = json.loads(args.voice_map.read_text(encoding='utf-8')) if args.voice_map else None
    print(json.dumps(build(args.catalog, args.model, args.out, args.cache, mapping), ensure_ascii=False))


if __name__ == '__main__':
    main()
