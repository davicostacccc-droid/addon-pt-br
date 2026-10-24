"""Read Lua literal tables only. Never evaluate Lua expressions or loaders."""
import re


class Reader:
    def __init__(self, text):
        self.text, self.pos = text, 0

    def space(self):
        while self.pos < len(self.text) and self.text[self.pos].isspace(): self.pos += 1

    def take(self, token):
        self.space()
        if not self.text.startswith(token, self.pos): raise ValueError(f'Expected {token} at {self.pos}')
        self.pos += len(token)

    def value(self, depth=0):
        if depth > 25: raise ValueError('Table nesting too deep')
        self.space()
        if self.pos >= len(self.text): raise ValueError('Truncated literal')
        char = self.text[self.pos]
        if char in '\"\'':
            quote = char
            self.pos += 1
            parts = []
            while self.pos < len(self.text):
                char = self.text[self.pos]; self.pos += 1
                if char == quote: return ''.join(parts)
                if char == '\\':
                    if self.pos >= len(self.text): raise ValueError('Truncated escape')
                    char = self.text[self.pos]; self.pos += 1
                    if char.isdigit() and char.isascii():
                        digits = char
                        while len(digits) < 3 and self.pos < len(self.text) and self.text[self.pos].isdigit() and self.text[self.pos].isascii():
                            digits += self.text[self.pos]; self.pos += 1
                        value = int(digits)
                        if value > 255: raise ValueError('Invalid byte escape')
                        parts.append(chr(value))
                    else:
                        escapes = {'n':'\n','r':'\r','t':'\t','a':'\a','b':'\b','f':'\f','v':'\v','\\':'\\','\"':'\"',"'":"'",'\n':'\n'}
                        if char not in escapes: raise ValueError('Unsupported escape')
                        parts.append(escapes[char])
                else: parts.append(char)
            raise ValueError('Unterminated string')
        if char == '{':
            self.pos += 1
            table, index = {}, 1
            while True:
                self.space()
                if self.pos < len(self.text) and self.text[self.pos] == '}':
                    self.pos += 1; return table
                if self.pos < len(self.text) and self.text[self.pos] == '[':
                    self.pos += 1; key = self.value(depth + 1); self.take(']'); self.take('=')
                else:
                    key = index; index += 1
                if key in table: raise ValueError('Duplicate table key')
                table[key] = self.value(depth + 1)
                self.space()
                if self.pos < len(self.text) and self.text[self.pos] in ',;': self.pos += 1
                elif self.pos >= len(self.text) or self.text[self.pos] != '}': raise ValueError('Expected table separator')
        match = re.match(r'(?:nil|true|false)\b|[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?', self.text[self.pos:])
        if not match: raise ValueError('Expressions are not data')
        self.pos += len(match[0]); token = match[0]
        if token == 'nil': return None
        if token in ('true','false'): return token == 'true'
        return float(token) if any(c in token.lower() for c in '.e') else int(token)


def literal(text):
    reader = Reader(text)
    value = reader.value()
    reader.space()
    if reader.pos != len(text): raise ValueError('Trailing code is not data')
    return value


def numeric_rows(text, quoted=False, only=None):
    pattern = r'^\s*\["(\d+)"\]\s*=\s*(\{.*\})\s*,?\s*$' if quoted else r'^\[(\d+)\]\s*=\s*(\{.*\})\s*,?\s*$'
    seen = set()
    for line in text.splitlines():
        match = re.match(pattern, line)
        if not match: continue
        key = int(match[1])
        if only is not None and key not in only: continue
        if key in seen: raise ValueError(f'Duplicate record {key}')
        seen.add(key)
        yield key, literal(match[2])
