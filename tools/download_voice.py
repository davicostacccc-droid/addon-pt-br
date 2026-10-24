"""Explicit one-time download; TTS generation itself is offline."""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://huggingface.co/rhasspy/piper-voices/resolve/main/pt/pt_BR/faber/medium/'
FILES = ['MODEL_CARD', 'pt_BR-faber-medium.onnx.json', 'pt_BR-faber-medium.onnx']


def main():
    parser = argparse.ArgumentParser(description='Baixa a voz neural brasileira Faber (cerca de 64 MB).')
    parser.add_argument('--out', type=Path, default=ROOT / 'models')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    results = []
    for name in FILES:
        target = args.out / name
        if not target.exists():
            part = target.with_suffix(target.suffix + '.part')
            with urllib.request.urlopen(BASE + name, timeout=120) as response, part.open('wb') as output:
                while block := response.read(1024 * 1024):
                    output.write(block)
            part.replace(target)
        with target.open('rb') as stream:
            checksum = hashlib.file_digest(stream, 'sha256').hexdigest()
        results.append({'file': name, 'sha256': checksum, 'source': BASE + name})
    (args.out / 'provenance.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
