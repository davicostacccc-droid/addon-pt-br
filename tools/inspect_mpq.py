"""Read-only MPQ inventory. Never installs patches or executes embedded Lua."""
import argparse
import bz2
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct
import zlib
import mpyq


def prefix(archive, block):
    if block.flags & 0x10000:
        raise ValueError('Encrypted blocks are not supported by this inspector.')
    stream = archive.file
    stream.seek(archive.header['offset'] + block.offset)
    if not block.flags & 0x200:
        return stream.read(min(4096, block.archived_size))
    if block.flags & 0x1000000:
        raise ValueError('Single-unit compressed blocks require a different reader.')
    start, end = struct.unpack('<II', stream.read(8))
    if not 8 <= start <= end <= block.archived_size:
        raise ValueError('Invalid first-sector bounds.')
    stream.seek(archive.header['offset'] + block.offset + start)
    data = stream.read(end - start)
    expected = min(512 << archive.header['sector_size_shift'], block.size)
    if len(data) < expected:
        if data[0] == 2:
            data = zlib.decompressobj().decompress(data[1:], expected + 1)
        elif data[0] == 16:
            data = bz2.BZ2Decompressor().decompress(data[1:], max_length=expected + 1)
        else:
            raise ValueError('Unsupported sector compression.')
    if len(data) > expected:
        raise ValueError('Decompressed sector exceeds its declared size.')
    return data[:4096]


def signature(data):
    text = data.removeprefix(b'\xef\xbb\xbf').lstrip()
    if data.startswith(b'RIFF'): return 'RIFF/WAV'
    if data.startswith(b'BLP'): return 'BLP texture'
    if data[:4] in (b'WDBC', b'WDB2'): return 'DBC table'
    if data.startswith(b'OggS'): return 'OGG'
    if data.startswith(b'ID3') or (len(data) > 1 and data[0] == 255 and data[1] & 224 == 224): return 'MP3'
    if text.startswith(b'<Ui'): return 'XML interface'
    if text.startswith((b'--', b'FADE_IN_TIME', b'00:')): return 'Lua/text/subtitle'
    return 'other'


def inspect(path, candidates=None):
    archive = mpyq.MPQArchive(str(path), listfile=False)
    counts, errors, identified = Counter(), [], []
    lookup = {(h.hash_a, h.hash_b): h.block_table_index for h in archive.hash_table
              if h.block_table_index < len(archive.block_table)}
    try:
        for index, block in enumerate(archive.block_table):
            if block.flags & 0x80000000 and block.archived_size:
                try: counts[signature(prefix(archive, block))] += 1
                except Exception as error: errors.append({'block': index, 'error': str(error)})
        for name in candidates or []:
            pair = archive._hash(name, 'HASH_A'), archive._hash(name, 'HASH_B')
            index = lookup.get(pair)
            if index is not None:
                identified.append({'path': name, 'block': index, 'bytes': archive.block_table[index].size})
        with path.open('rb') as stream:
            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        return {'archive': path.name, 'sha256': digest,
                'block_entries': len(archive.block_table), 'signatures': dict(counts),
                'matched_paths': identified, 'read_errors': errors,
                'limitations': ['Signatures do not verify every sector or playback.',
                                'Matched paths do not prove the spoken language.',
                                'This inventory does not confirm client compatibility.']}
    finally:
        archive.file.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Inventaria um MPQ sem instalar ou modificar o arquivo.')
    parser.add_argument('archive', type=Path)
    parser.add_argument('--names', type=Path, help='Candidate archive paths, one per line')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists(): parser.error('Escolha um arquivo de saída novo.')
    names = args.names.read_text(encoding='utf-8-sig').splitlines() if args.names else []
    report = inspect(args.archive, names)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'matched_paths'}, ensure_ascii=True, indent=2))
    print('Matched paths:', len(report['matched_paths']))
