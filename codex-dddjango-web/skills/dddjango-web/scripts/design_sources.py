"""Static dependency discovery; no evaluation of template expressions or JSX."""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import PurePosixPath
import re
import urllib.parse

IMAGE_SUFFIXES = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'}


def resource_kind(source: str, default: str = 'file') -> str:
    suffix = PurePosixPath(urllib.parse.urlsplit(source).path).suffix.lower()
    if source.startswith('data:image/') or suffix in IMAGE_SUFFIXES:
        return 'image'
    return {'.css': 'css', '.js': 'script', '.mjs': 'script', '.jsx': 'component', '.tsx': 'component',
            '.html': 'html', '.htm': 'html', '.woff': 'font', '.woff2': 'font', '.ttf': 'font', '.otf': 'font'}.get(suffix, default)


def css_dependencies(source: str) -> list[tuple[str, str, str]]:
    source = re.sub(r'/\*.*?\*/', '', source, flags=re.S)
    imports = re.findall(r'@import\s+(?:url\(\s*)?[\'"]([^\'"]+)[\'"]', source, flags=re.I)
    rows = [(value, 'css', 'file') for value in imports]
    for match in re.finditer(r'url\(\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s)]+))\s*\)', source, flags=re.I):
        value = next((part for part in match.groups() if part is not None), '')
        if value and not value.startswith('#') and value not in imports:
            rows.append((value, resource_kind(value, 'image'), 'file'))
    return rows


class Dependencies(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows = []
        self.in_style = False
        self.in_script = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('style'):
            self.rows.extend((ref, kind, 'document') for ref, kind, _base in css_dependencies(attrs['style']))
        if tag == 'style':
            self.in_style = True
        if tag == 'script' and not attrs.get('src'):
            self.in_script = True
        attribute = None
        kind = 'file'
        if tag in ('img', 'script', 'source', 'video', 'audio', 'iframe'):
            attribute = 'src'
            kind = {'img': 'image', 'script': 'script', 'iframe': 'html'}.get(tag, 'file')
        elif tag == 'link' and attrs.get('rel', '').lower() in ('stylesheet', 'icon', 'preload', 'modulepreload'):
            attribute = 'href'
            kind = 'css' if attrs.get('rel', '').lower() == 'stylesheet' else 'file'
        elif tag == 'x-import':
            attribute, kind = 'from', 'component'
        elif tag == 'a' and 'download' in attrs:
            attribute = 'href'
        if attribute and attrs.get(attribute):
            value = attrs[attribute]
            self.rows.append((value, resource_kind(value, kind), 'file' if tag == 'x-import' else 'document'))
        if tag == 'video' and attrs.get('poster'):
            self.rows.append((attrs['poster'], 'image', 'document'))
        if attrs.get('srcset'):
            # A data URI contains commas; require explicit resolution instead of mis-splitting it.
            if attrs['srcset'].startswith('data:'):
                self.rows.append(('{srcset data URI requires explicit acquisition}', 'image', 'document'))
            else:
                self.rows.extend((item.strip().split()[0], 'image', 'document') for item in attrs['srcset'].split(',') if item.strip())

    def handle_endtag(self, tag):
        if tag == 'style':
            self.in_style = False
        if tag == 'script':
            self.in_script = False

    def handle_data(self, data):
        if self.in_style:
            self.rows.extend((ref, kind, 'document') for ref, kind, _base in css_dependencies(data))
        elif self.in_script:
            self.rows.extend(es_dependencies(data))


_JS_TOKEN = re.compile(
    r'''(?P<space>\s+)|(?P<comment>//[^\n]*|/\*.*?\*/)|'''
    r'''(?P<string>"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')|'''
    r'''(?P<identifier>[A-Za-z_$][\w$]*)|(?P<punct>.)''', re.S)


def _skip_quoted(source: str, start: int, quote: str) -> int:
    index = start + 1
    while index < len(source):
        if source[index] == '\\':
            index += 2
        elif source[index] == quote:
            return index + 1
        else:
            index += 1
    return len(source)


def _interpolation_end(source: str, start: int) -> int | None:
    depth = 1
    index = start
    while index < len(source):
        if source.startswith('//', index):
            newline = source.find('\n', index + 2)
            index = len(source) if newline < 0 else newline + 1
        elif source.startswith('/*', index):
            end = source.find('*/', index + 2)
            index = len(source) if end < 0 else end + 2
        elif source[index] in ('\'', '"', '`'):
            index = _skip_quoted(source, index, source[index])
        elif source[index] == '{':
            depth += 1
            index += 1
        elif source[index] == '}':
            depth -= 1
            if depth == 0:
                return index
            index += 1
        else:
            index += 1
    return None


def _template_code(source: str) -> tuple[str, bool]:
    """Blank inert template chunks and append executable interpolation code."""
    output = list(source)
    interpolations: list[str] = []
    invalid = False
    index = 0
    while index < len(source):
        if source.startswith('//', index):
            newline = source.find('\n', index + 2)
            index = len(source) if newline < 0 else newline + 1
        elif source.startswith('/*', index):
            end = source.find('*/', index + 2)
            index = len(source) if end < 0 else end + 2
        elif source[index] in ('\'', '"'):
            index = _skip_quoted(source, index, source[index])
        elif source[index] == '`':
            cursor = index + 1
            closed = False
            while cursor < len(source):
                if source[cursor] == '\\':
                    cursor += 2
                elif source.startswith('${', cursor):
                    end = _interpolation_end(source, cursor + 2)
                    if end is None:
                        invalid = True
                        cursor = len(source)
                        break
                    interpolations.append(source[cursor + 2:end])
                    cursor = end + 1
                elif source[cursor] == '`':
                    cursor += 1
                    closed = True
                    break
                else:
                    cursor += 1
            if not closed:
                invalid = True
            output[index:cursor] = 'T' + ' ' * (cursor - index - 1)
            index = cursor
        else:
            index += 1
    prepared = ''.join(output)
    for interpolation in interpolations:
        nested, nested_invalid = _template_code(interpolation)
        prepared += '\n' + nested
        invalid = invalid or nested_invalid
    return prepared, invalid


_REGEX_LITERAL = re.compile(
    r'''/(?P<body>(?:\\.|\[(?:\\.|[^\]\\])*\]|[^/\n\\])*)/[A-Za-z]*''')


def _mask_regex_literals(source: str) -> str:
    """Blank regex literals while preserving strings/comments and later code."""
    output = list(source)
    can_start_regex = True
    index = 0
    prefix_words = {'return', 'throw', 'case', 'yield', 'delete', 'void', 'typeof',
                    'instanceof', 'in', 'of', 'else', 'do'}
    prefix_punctuation = set('([{=,:;!?&|+-*%^~<>')
    while index < len(source):
        if source[index].isspace():
            index += 1
        elif source.startswith('//', index):
            newline = source.find('\n', index + 2)
            index = len(source) if newline < 0 else newline + 1
        elif source.startswith('/*', index):
            end = source.find('*/', index + 2)
            index = len(source) if end < 0 else end + 2
        elif source[index] in ('\'', '"'):
            index = _skip_quoted(source, index, source[index])
            can_start_regex = False
        elif source[index] == '/' and can_start_regex:
            match = _REGEX_LITERAL.match(source, index)
            if match:
                output[index:match.end()] = ' ' * (match.end() - index)
                index = match.end()
                can_start_regex = False
            else:
                index += 1
                can_start_regex = True
        elif source[index].isalpha() or source[index] in ('_', '$'):
            end = index + 1
            while end < len(source) and (source[end].isalnum() or source[end] in ('_', '$')):
                end += 1
            can_start_regex = source[index:end] in prefix_words
            index = end
        elif source[index].isdigit():
            index += 1
            while index < len(source) and (source[index].isalnum() or source[index] in '._'):
                index += 1
            can_start_regex = False
        elif source.startswith(('++', '--'), index):
            # Prefix keeps an operand-required context; postfix keeps a completed operand.
            index += 2
        else:
            can_start_regex = source[index] in prefix_punctuation
            index += 1
    return ''.join(output)


def es_dependencies(source: str) -> list[tuple[str, str, str]]:
    """Find supported ES literal edges and explicit unsupported source forms.

    This deliberately is not a JavaScript evaluator. Token context prevents
    comments and string contents from manufacturing fake import statements.
    """
    prepared, invalid_template = _template_code(source)
    prepared = _mask_regex_literals(prepared)
    tokens = [(match.lastgroup, match.group()) for match in _JS_TOKEN.finditer(prepared)
              if match.lastgroup not in ('space', 'comment')]
    rows: list[tuple[str, str, str]] = []
    if invalid_template:
        rows.append(('{unsupported template interpolation}', 'script', 'file'))

    def literal(index: int) -> str | None:
        if index < len(tokens) and tokens[index][0] == 'string':
            quoted = tokens[index][1]
            return re.sub(r'\\([\\\'"/])', r'\1', quoted[1:-1])
        return None

    def add(value: str) -> None:
        if value.startswith(('.', '/', 'http:', 'https:')):
            rows.append((value, resource_kind(value, 'script'), 'file'))
        else:
            rows.append(('{bare module:' + value + '}', 'script', 'file'))

    i = 0
    while i < len(tokens):
        kind, value = tokens[i]
        if kind == 'identifier' and value == 'import' and (i == 0 or tokens[i - 1][1] != '.'):
            if i + 1 < len(tokens) and tokens[i + 1][1] == '(':
                dep = literal(i + 2)
                if dep is None or i + 3 >= len(tokens) or tokens[i + 3][1] != ')':
                    rows.append(('{non-literal import}', 'script', 'file'))
                else:
                    add(dep)
            else:
                dep = literal(i + 1)
                if dep is not None:
                    add(dep)
                else:
                    j = i + 1
                    while j < len(tokens) and tokens[j][1] not in (';',):
                        if tokens[j] == ('identifier', 'from'):
                            dep = literal(j + 1)
                            break
                        j += 1
                    if dep is not None:
                        add(dep)
        elif kind == 'identifier' and value == 'export':
            j = i + 1
            while j < len(tokens) and tokens[j][1] != ';':
                if tokens[j] == ('identifier', 'from'):
                    dep = literal(j + 1)
                    if dep is not None:
                        add(dep)
                    break
                j += 1
        i += 1
    # JSX resource expressions are outside the literal acquisition boundary.
    code_context = ' '.join(value if kind != 'string' else ' ' * len(value) for kind, value in tokens)
    if re.search(r'\b(?:src|href|poster)\s*=\s*\{', code_context):
        rows.append(('{JSX resource expression}', 'file', 'file'))
    return rows


def dependencies(source: str, kind: str) -> list[tuple[str, str, str]]:
    if kind == 'css':
        rows = css_dependencies(source)
    elif kind in ('html', 'component', 'script'):
        parser = Dependencies()
        if kind != 'script':
            parser.feed(source)
        rows = parser.rows
        if kind in ('script', 'component'):
            rows.extend(es_dependencies(source))
    else:
        return []
    return list(dict.fromkeys(rows))
