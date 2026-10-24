"""Read a quest translation dump as data. Never execute SQL or connect to a DB.

The output is a staging index, NOT an installable 3.3.5 voice catalog.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

HEADER = re.compile(r'INSERT\s+INTO\s+`quest_template_locale`\s*\((.*?)\)\s*VALUES', re.I | re.S)
FIELDS = ('Title', 'Details', 'Objectives', 'EndText', 'CompletedText',
          'ObjectiveText1', 'ObjectiveText2', 'ObjectiveText3', 'ObjectiveText4')


def read_rows(sql, table='quest_template_locale'):
    """Parse INSERT literals only, including escaped quotes and embedded commas."""
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', table):
        raise ValueError('Invalid table name.')
    pattern = re.compile(r'INSERT\s+INTO\s+`' + table + r'`\s*(?:\((.*?)\)\s*)?VALUES', re.I | re.S)
    for header in pattern.finditer(sql):
        if header.group(1):
            columns = re.findall(r'`([^`]+)`', header.group(1))
        else:
            schema = re.search(r'CREATE TABLE(?: IF NOT EXISTS)?\s+`' + table + r'`\s*\((.*?)\n\)', sql, re.I | re.S)
            if not schema:
                raise ValueError('INSERT without columns requires a CREATE TABLE schema.')
            columns = re.findall(r'^\s*`([^`]+)`', schema.group(1), re.M)
        pos = header.end()

        def spaces():
            nonlocal pos
            while pos < len(sql) and sql[pos].isspace():
                pos += 1

        def value():
            nonlocal pos
            spaces()
            if sql[pos] != "'":
                match = re.match(r'(NULL|[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)\b', sql[pos:pos + 64], re.I)
                if not match:
                    raise ValueError('Only integer, NULL and string literals are supported.')
                pos += match.end()
                if match[0].upper() == 'NULL': return None
                return float(match[0]) if any(c in match[0].lower() for c in '.e') else int(match[0])
            pos += 1
            result = []
            while pos < len(sql):
                char = sql[pos]
                pos += 1
                if char == "'":
                    if pos < len(sql) and sql[pos] == "'":
                        result.append("'"); pos += 1
                    else:
                        return ''.join(result)
                elif char == '\\':
                    if pos >= len(sql):
                        break
                    char = sql[pos]; pos += 1
                    result.append({'n': '\n', 'r': '\r', 't': '\t', '0': '\0', 'Z': '\x1a'}.get(char, char))
                else:
                    result.append(char)
            raise ValueError('Unterminated SQL string.')

        while True:
            spaces()
            if pos >= len(sql) or sql[pos] != '(':
                raise ValueError('Expected literal row.')
            pos += 1
            row = []
            while True:
                row.append(value()); spaces()
                if sql[pos] == ')':
                    pos += 1; break
                if sql[pos] != ',':
                    raise ValueError('Invalid SQL row separator.')
                pos += 1
            if len(row) != len(columns):
                raise ValueError('Row width does not match INSERT columns.')
            yield dict(zip(columns, row))
            spaces()
            if pos < len(sql) and sql[pos] == ';':
                break
            if pos >= len(sql) or sql[pos] != ',':
                raise ValueError('Expected comma or end of INSERT.')
            pos += 1


def audit(sql):
    records, builds, populated, suspicious = {}, Counter(), Counter(), Counter()
    english = re.compile(r'\b(the|you|your|return to|speak to|kill|bring|collect)\b', re.I)
    for row in read_rows(sql):
        if row.get('locale') != 'ptBR':
            continue
        quest_id = row['ID']
        if type(quest_id) is not int or quest_id <= 0 or str(quest_id) in records:
            raise ValueError('Invalid or duplicate quest ID.')
        records[str(quest_id)] = {field: row.get(field) for field in FIELDS}
        records[str(quest_id)]['VerifiedBuild'] = row.get('VerifiedBuild')
        builds[str(row.get('VerifiedBuild'))] += 1
        for field in FIELDS:
            text = row.get(field)
            if text:
                populated[field] += 1
                if english.search(text):
                    suspicious[field] += 1
    if not records:
        raise ValueError('No ptBR quest records found.')
    return {'version': 1, 'kind': 'quest-translation-staging', 'quests': records}, {
        'quest_records': len(records), 'source_builds': dict(builds),
        'nonempty_fields': dict(populated), 'possible_english_fields_heuristic': dict(suspicious),
        'playable': False, 'gossip_records': 0,
        'pending': ['English 3.3.5 source texts and exact matching', 'NPC and quest relations',
                    'Classic versus original 3.3.5 content validation', 'Player placeholders and gender',
                    'Reward and progress texts from separate tables', 'Voice generation']}


def main():
    parser = argparse.ArgumentParser(description='Importa traduções de quests em lote para análise local.')
    parser.add_argument('input', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--source-url', default='')
    args = parser.parse_args()
    if args.out.exists():
        parser.error('Escolha uma pasta de saída nova.')
    raw = args.input.read_bytes()
    index, report = audit(raw.decode('utf-8-sig'))
    report['source_url'] = args.source_url
    report['source_sha256'] = hashlib.sha256(raw).hexdigest()
    args.out.mkdir(parents=True)
    (args.out / 'quest-translations.json').write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding='utf-8')
    (args.out / 'audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
