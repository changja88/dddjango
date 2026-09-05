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

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('style'):
            self.rows.extend((ref, kind, 'document') for ref, kind, _base in css_dependencies(attrs['style']))
        if tag == 'style':
            self.in_style = True
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

    def handle_data(self, data):
        if self.in_style:
            self.rows.extend((ref, kind, 'document') for ref, kind, _base in css_dependencies(data))


def dependencies(source: str, kind: str) -> list[tuple[str, str, str]]:
    if kind == 'css':
        rows = css_dependencies(source)
    elif kind in ('html', 'component', 'script'):
        parser = Dependencies()
        if kind != 'script':
            parser.feed(source)
        rows = parser.rows
        if kind in ('script', 'component'):
            # Literal ES imports only; dynamic expressions cannot be resolved by static freezing.
            code = re.sub(r'/\*.*?\*/|^\s*//[^\n]*', '', source, flags=re.S | re.M)
            for match in re.finditer(r'\b(?:from\s*|import\s*(?:\(\s*)?)[\'"]([^\'"]+)[\'"]', code):
                value = match[1]
                rows.append((value if value.startswith(('.', '/', 'http:', 'https:')) else '{module:' + value + '}', resource_kind(value, 'script'), 'file'))
    else:
        return []
    return list(dict.fromkeys(rows))
