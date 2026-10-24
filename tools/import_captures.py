"""Turn copied JSON into a translation queue; never parse/execute SavedVariables."""
import argparse
import json
from pathlib import Path
from build_pack import validate_row, normalize


def main():
    parser = argparse.ArgumentParser(description='Importa JSON copiado de /avoz exportar.')
    parser.add_argument('input', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error('Arquivo de saída já existe. Escolha outro nome para preservar seus dados.')
    data = json.loads(args.input.read_text(encoding='utf-8-sig'))
    if data.get('version') != 1 or not isinstance(data.get('lines'), list):
        parser.error('Formato de captura inválido.')
    lines, seen = [], set()
    for row in data['lines']:
        validate_row(row, translated=False)
        identity = row['event'], row['npc'], normalize(row['source'])
        if identity in seen:
            continue
        seen.add(identity)
        # Whitelist fields; paths or executable content have no special meaning.
        lines.append({k: row[k] for k in ('event', 'npc', 'source', 'title', 'questID') if k in row})
        lines[-1]['translation'] = ''
    args.out.write_text(json.dumps({'version': 1, 'lines': lines}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'{len(lines)} falas importadas. Traduza e revise antes de gerar o pacote.')


if __name__ == '__main__':
    main()
