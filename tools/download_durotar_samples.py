"""Retrieve only a small test selection from the official public ptBR ZIP."""
import hashlib
import json
from pathlib import Path
import zipfile
from http_range_zip import HttpRangeReader

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://mediafilez.forgecdn.net/files/6516/696/AI_VoiceOverData_Vanilla_ptBR_v0.1.zip'
SIZE = 2084719906
QUESTS = (4641, 788, 789, 790, 804, 4402)


def main():
    output = ROOT / 'research' / 'voiceover-ptbr' / 'audio'
    output.mkdir(parents=True, exist_ok=True)
    remote = HttpRangeReader(URL, SIZE)
    records = []
    with zipfile.ZipFile(remote) as archive:
        names = set(archive.namelist())
        for quest in QUESTS:
            for phase in ('accept', 'progress', 'complete'):
                filename = f'{quest}-{phase}.mp3'
                entry = 'AI_VoiceOverData_Vanilla_ptBR/generated/sounds/quests/' + filename
                if entry not in names: continue
                path = output / filename
                if not path.exists():
                    data = archive.read(entry)  # ZipFile also checks the member CRC.
                    path.write_bytes(data)
                records.append({'file': filename, 'source_entry': entry,
                    'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size})
    report = {'source_url': URL, 'official_file_id': 6516696, 'bytes_downloaded': remote.transferred,
              'files': records, 'note': 'Local inspection/test only; no upstream Lua was executed.'}
    (output.parent / 'selected-audio-provenance.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({'files': len(records), 'bytes_downloaded': remote.transferred}))


if __name__ == '__main__': main()
