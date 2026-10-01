#!/usr/bin/env python3
"""v4 원본 census의 정확값 → foundation 토큰 후보 시트. 표준 라이브러리, 비게이트.

비교기의 시각 허용 오차를 사용하지 않는다. CSS 문맥을 알 수 없는 값은 추측하지
않고 신규 등록 필요/수동 확인으로 남긴다. 파일·토큰·앱 코드를 고치지 않는다.
"""
from __future__ import annotations

import argparse
import collections
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re
import sys


def split_css(value: str, separators: str) -> list[str]:
    """따옴표·함수 안을 보존해 최상위 구분자로 나눈다. 주석은 공백이다."""
    parts, buf = [], []
    quote, depth, i = '', 0, 0
    while i < len(value):
        ch = value[i]
        if quote:
            buf.append(ch)
            if ch == '\\' and i + 1 < len(value):
                i += 1
                buf.append(value[i])
            elif ch == quote:
                quote = ''
        elif value.startswith('/*', i):
            end = value.find('*/', i + 2)
            if end < 0:
                raise ValueError('unterminated CSS comment')
            buf.append(' ')
            i = end + 1
        elif ch in ('"', "'"):
            quote = ch
            buf.append(ch)
        elif ch == '(':
            depth += 1
            buf.append(ch)
        elif ch == ')':
            depth -= 1
            if depth < 0:
                raise ValueError('unbalanced CSS function')
            buf.append(ch)
        elif depth == 0 and ch in separators:
            if ''.join(buf).strip():
                parts.append(''.join(buf).strip())
            buf = []
        else:
            buf.append(ch)
        i += 1
    if quote or depth:
        raise ValueError('unterminated CSS string/function')
    if ''.join(buf).strip():
        parts.append(''.join(buf).strip())
    return parts


def token_values(css: str) -> dict[str, str | None]:
    declarations: dict[str, set[str]] = collections.defaultdict(set)
    for part in split_css(css, '{};'):
        match = re.fullmatch(r'(--[\w-]+)\s*:\s*(.+)', part, re.S)
        if match:
            declarations[match[1]].add(re.sub(r'\s*!important\s*$', '', match[2]).strip())
    resolved: dict[str, str | None] = {}

    def resolve(name: str, trail: frozenset[str]) -> str | None:
        if name in trail:
            return None
        if name in resolved:
            return resolved[name]
        values = declarations.get(name, set())
        if len(values) != 1:
            resolved[name] = None
            return None
        value = next(iter(values))
        failed = False

        def replace(match: re.Match) -> str:
            nonlocal failed
            target = resolve(match[1], trail | {name})
            if target is None:
                failed = True
                return ''
            return target

        value = re.sub(r'var\(\s*(--[\w-]+)\s*\)', replace, value)
        if failed or re.search(r'\b(?:var|calc|env|clamp|min|max)\(', value):
            value = None
        resolved[name] = value
        return value

    for name in sorted(declarations):
        resolve(name, frozenset())
    return resolved


def color(value: str) -> tuple | None:
    try:
        return _color(value)
    except (ValueError, ZeroDivisionError):
        return None


def _color(value: str) -> tuple | None:
    if value.startswith('color-mix(') and value.endswith(')'):
        parts = split_css(value[10:-1], ',')
        if len(parts) != 3 or parts[0] != 'in srgb':
            return None
        colors, weights = [], []
        for part in parts[1:]:
            pieces = split_css(part, ' \t\n')
            weight = Fraction(pieces.pop()[:-1]) / 100 if pieces[-1].endswith('%') else None
            operand = color(' '.join(pieces))
            if operand is None or (weight is not None and not 0 <= weight <= 1):
                return None
            # Legacy rgb/hex operands enter interpolation with byte channels/alpha.
            if operand[-1] == 'rgb':
                operand = ('color', *(byte(x) for x in operand[1:4]),
                           Fraction(byte(operand[4] * 255), 255), 'rgb')
            colors.append(operand)
            weights.append(weight)
        a, b = weights
        if a is None and b is None:
            a = b = Fraction(1, 2)
        elif a is None:
            a = 1 - b
        elif b is None:
            b = 1 - a
        total = a + b
        if not total:
            return None
        a, b = a / total, b / total
        alpha = colors[0][4] * a + colors[1][4] * b
        channels = tuple((colors[0][i] * colors[0][4] * a + colors[1][i] * colors[1][4] * b) / alpha
                         if alpha else Fraction(0) for i in (1, 2, 3))
        return ('color', *channels, alpha * min(total, 1), 'srgb')
    if re.fullmatch(r'#[0-9a-fA-F]{3,4}|#[0-9a-fA-F]{6}(?:[0-9a-fA-F]{2})?', value):
        digits = value[1:]
        if len(digits) in (3, 4):
            digits = ''.join(ch * 2 for ch in digits)
        channels = tuple(Fraction(int(digits[i:i + 2], 16)) for i in (0, 2, 4))
        alpha = Fraction(int(digits[6:8], 16), 255) if len(digits) == 8 else Fraction(1)
        return ('color', *channels, alpha, 'rgb')
    match = re.fullmatch(r'(rgba?|color)\((.*)\)', value, re.I)
    if not match:
        return {'transparent': ('color', Fraction(0), Fraction(0), Fraction(0), Fraction(0), 'rgb')}.get(value)
    body = match[2].strip()
    srgb = match[1].lower() == 'color'
    if srgb:
        if not body.startswith('srgb '):
            return None
        body = body[5:]
    parts = re.split(r'[\s,/]+', body)
    if len(parts) not in (3, 4):
        return None
    try:
        channels = tuple(Fraction(p.rstrip('%')) * (Fraction(255, 100) if p.endswith('%') else 255 if srgb else 1) for p in parts[:3])
        alpha = Fraction(parts[3].rstrip('%')) / (100 if parts[3].endswith('%') else 1) if len(parts) == 4 else Fraction(1)
    except ValueError:
        return None
    if not all(0 <= channel <= 255 for channel in channels) or not 0 <= alpha <= 1:
        return None
    return ('color', *channels, alpha, 'srgb' if srgb else 'rgb')


def byte(value: Fraction) -> int:
    return int(value + Fraction(1, 2))


def color_formats(tree: tuple) -> tuple[str, ...]:
    if tree[0] == 'color':
        return (tree[-1],)
    return tuple(mode for part in tree if isinstance(part, tuple) for mode in color_formats(part))


def serialized(tree: tuple, formats: tuple[str, ...]) -> tuple:
    """관측 형식으로 직렬화한다. srgb의 6자리와 legacy rgb의 byte 정밀도를 구별한다."""
    modes = iter(formats)

    def visit(node: tuple) -> tuple:
        if node[0] == 'color':
            mode = next(modes)
            if mode == 'srgb':
                return ('color', *(format(float(x / 255), '.6g') for x in node[1:4]),
                        format(float(node[4]), '.6g'))
            return ('color', *(byte(x) for x in node[1:4]), byte(node[4] * 255))
        return tuple(visit(part) if isinstance(part, tuple) else part for part in node)

    return visit(tree)


def atom(value: str) -> tuple | None:
    colour = color(value)
    if colour is not None:
        return colour
    match = re.fullmatch(r'([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)([a-zA-Z%]*)', value)
    if match:
        number, unit = Fraction(match[1]), match[2].lower()
        if unit in ('rem', 'em', 'vw', 'vh', 'vmin', 'vmax', 'ch', 'ex', 'lh', 'rlh'):
            return None
        if number == 0 and unit == 'px':
            unit = ''
        return ('number', number, unit)
    match = re.fullmatch(r'([\w-]+)\((.*)\)', value, re.S)
    if match:
        if match[1].lower() not in ('blur', 'brightness', 'contrast', 'grayscale',
                                   'hue-rotate', 'invert', 'opacity', 'saturate', 'sepia'):
            return None
        inner = canonical(match[2], '')
        return ('function', match[1].lower(), inner) if inner is not None else None
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return ('word', value[1:-1])
    return ('word', value)


@lru_cache(maxsize=16384)
def canonical(value: str, prop: str) -> tuple | None:
    try:
        return _canonical(value, prop)
    except ValueError:
        # v4는 bgi/content/mask 문자열에 상한을 둔다. 잘린 값은 정확 일치가 아니다.
        return None


def _canonical(value: str, prop: str) -> tuple | None:
    if prop == 'ff':
        value = split_css(value, ',')[0]
        if '\\' in value or '/' in value or re.match(r'\d', value):
            return None
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        return ('font', ' '.join(value.split()))
    layers = []
    for layer in split_css(value, ','):
        parts = [atom(part) for part in split_css(layer, ' \t\r\n')]
        if not parts or any(part is None for part in parts):
            return None
        if prop == 'sh' and parts != [('word', 'none')]:
            colours = [part for part in parts if part[0] == 'color']
            lengths = [part for part in parts if part[0] == 'number' and (part[2] == 'px' or part[1:] == (0, ''))]
            inset = ('word', 'inset') in parts
            if len(colours) != 1 or not 2 <= len(lengths) <= 4 or len(parts) != 1 + len(lengths) + int(inset):
                return None
            lengths += [('number', Fraction(0), '')] * (4 - len(lengths))
            parts = [*colours, *lengths, ('inset', inset)]
        elif prop in ('pad', 'rad') and 1 <= len(parts) <= 4:
            a = parts[0]
            b = parts[1] if len(parts) > 1 else a
            c = parts[2] if len(parts) > 2 else a
            d = parts[3] if len(parts) > 3 else b
            parts = [a, b, c, d]
        elif prop == 'gap' and len(parts) == 1:
            parts *= 2
        layers.append(tuple(parts))
    return tuple(layers) if layers else None


def value_rows(styles: dict) -> list[tuple[str, str]]:
    rows = []
    for prop, raw in sorted(styles.items()):
        value = str(raw)
        if prop != 'bd':
            rows.append((prop, value))
        if prop == 'bd':
            sides = value.split('|')
            if len(sides) == 4:
                sides = [part.strip() for part in sides]
                entries = [('all', sides[0])] if len(set(sides)) == 1 else zip(('top', 'right', 'bottom', 'left'), sides)
                for side, part in entries:
                    part = part.strip()
                    rows.append((f'bd.{side}', part))
                    pieces = split_css(part, ' \t')
                    if len(pieces) == 3:
                        rows.extend([(f'bd.{side}.width', pieces[0]), (f'bd.{side}.color', pieces[2])])
        elif prop in ('pad', 'rad', 'gap'):
            pieces = split_css(value, ' \t')
            names = ('row', 'column') if prop == 'gap' else ('top-left', 'top-right', 'bottom-right', 'bottom-left') if prop == 'rad' else ('top', 'right', 'bottom', 'left')
            if len(pieces) == len(names) and len(set(pieces)) > 1:
                rows.extend((f'{prop}.{name}', part) for name, part in zip(names, pieces))
        elif prop in ('bf', 'fil'):
            match = re.fullmatch(r'blur\(([^()]+)\)', value)
            if match:
                rows.append((prop + '.blur', match[1]))
    defaults = {'none', 'auto', 'normal', 'visible', 'static', 'flow', 'normal normal'}
    return [(prop, value) for prop, value in rows if prop not in ('lines', 'src')
            and value not in defaults and not re.fullmatch(r'(?:0(?:px|%)?\s*)+', value)
            and not (prop == 'op' and value == '1')
            and not (color(value) is not None and color(value)[4] == 0)]


def inline(value: object) -> str:
    return '`' + str(value).replace('`', '&#96;').replace('|', '&#124;').replace('\n', ' ') + '`'


def category(prop: str) -> str:
    if prop in ('bg', 'c', 'fill', 'stroke') or prop.endswith('.color'):
        return 'color'
    if prop.endswith('.width'):
        return 'border-width'
    root = prop.split('.')[0]
    return {'fs': 'font-size', 'fw': 'font-weight', 'ff': 'font', 'lh': 'line-height',
            'ls': 'tracking', 'rad': 'radius', 'pad': 'space', 'gap': 'space',
            'sh': 'shadow', 'bd': 'border', 'ol': 'border', 'op': 'opacity',
            'minw': 'size', 'minh': 'size', 'maxw': 'size', 'maxh': 'size',
            'bf': 'blur' if prop.endswith('.blur') else 'filter',
            'fil': 'blur' if prop.endswith('.blur') else 'filter', 'bgi': 'image'}.get(root, root)


LENGTH_CATEGORIES = {'font-size', 'line-height', 'tracking', 'radius', 'space', 'border-width', 'size', 'blur'}


def token_category(name: str, raw: str | None) -> str:
    """값 종류를 먼저 확인하고 같은 단위 안의 용도 혼동은 이름으로 좁힌다."""
    if raw is not None:
        if color(raw) is not None or raw.startswith(('color(', 'color-mix(', 'hsl(', 'hsla(', 'lab(', 'oklab(', 'lch(', 'oklch(')):
            return 'color'
        shadow = canonical(raw, 'sh')
        if shadow and any(part[0] == 'color' for layer in shadow for part in layer):
            return 'shadow'
        if re.search(r'\b(solid|dashed|dotted|double)\b', raw):
            return 'border'
        if 'gradient(' in raw or 'url(' in raw:
            return 'image'
        if re.match(r'(blur|brightness|contrast|grayscale|hue-rotate|invert|opacity|saturate|sepia)\(', raw):
            return 'filter'
        if re.fullmatch(r'[A-Za-z-]+', raw):
            return 'font' if 'font' in name else 'unknown'
    for pattern, kind in (
        (r'(?:^|-)fs(?:-|$)|font-size', 'font-size'),
        (r'(?:^|-)fw(?:-|$)|font-weight|weight', 'font-weight'),
        (r'(?:^|-)lh(?:-|$)|line-height|leading', 'line-height'),
        (r'(?:^|-)ls(?:-|$)|letter-spacing|tracking', 'tracking'),
        (r'radius|(?:^|-)rad(?:-|$)|^--r\d+$', 'radius'),
        (r'padding|(?:^|-)(?:space|gap|pad)(?:-|$)', 'space'),
        (r'border|stroke-width|ring-width', 'border-width'),
        (r'opacity', 'opacity'), (r'(?:^|-)z(?:-|$)|z-index', 'z'),
        (r'blur', 'blur'), (r'font', 'font'), (r'width|height', 'size'),
    ):
        if re.search(pattern, name):
            return kind
    if raw is None:
        return 'unknown'
    if raw.startswith(('"', "'")):
        return 'font'
    if re.search(r'\d(?:px|rem|em|vw|vh|%)\b', raw) or raw.startswith(('calc(', 'clamp(', 'min(', 'max(')):
        return 'length'
    return 'unknown'


class TokenIndex:
    def __init__(self, css: str | None):
        self.tokens = [(name, raw, token_category(name, raw)) for name, raw in token_values(css or '').items()]
        self.indices = {}

    @lru_cache(maxsize=8192)
    def lookup(self, prop: str, value: str, capped: bool = False) -> str:
        if capped:
            return '수동 확인(v4 길이 상한)'
        normal_prop = prop if prop in ('ff', 'sh', 'pad', 'rad', 'gap') else ''
        target = canonical(value, normal_prop)
        if target is None:
            return '수동 확인(지원 밖 관측 표현)'
        formats = color_formats(target)
        key = (category(prop), normal_prop, formats)
        if key not in self.indices:
            index, unknown = collections.defaultdict(list), 0
            for name, raw, kind in self.tokens:
                if kind not in (key[0], 'unknown') and not (kind == 'length' and key[0] in LENGTH_CATEGORIES):
                    continue
                form = canonical(raw, normal_prop) if raw is not None else None
                if kind == 'unknown' and raw is not None and re.fullmatch(r'[A-Za-z-]+', raw):
                    if raw in ('none', 'auto', 'normal', 'visible', 'static', 'flow'):
                        continue
                    # Named colours / contextual keywords are not a proven missing token.
                    form = None
                if form is None:
                    unknown += 1
                elif len(color_formats(form)) == len(formats):
                    index[serialized(form, formats)].append(name)
            self.indices[key] = index, unknown
        index, unknown = self.indices[key]
        matches = sorted(index.get(serialized(target, formats), ()), key=lambda name: (len(name), name))
        if matches:
            result = ', '.join(inline(name) for name in matches[:6])
            if len(matches) > 6:
                result += f' 외 {len(matches) - 6}개(tokens.css 확인)'
            return ('첫 서체 일치(스택 확인): ' if prop == 'ff' else '') + result
        return f'수동 확인 — 해석 못 한 토큰 {unknown}개' if unknown else '신규 등록 필요'


def sample_refs(values: set[str]) -> str:
    return f'{len(values)}개: ' + (', '.join(inline(value) for value in sorted(values)[:2]) or '없음')


def render_sheet(censuses: dict, css: str | None) -> str:
    tokens = TokenIndex(css)
    groups = collections.defaultdict(list)
    records_by_case = {}
    children_by_case = {}
    if not isinstance(censuses, dict) or not censuses:
        raise ValueError('census must contain cases')
    for case, census in sorted(censuses.items()):
        meta, records = census['meta'], census['records']
        if meta.get('census_version') != 4 or meta.get('root_matched') not in (1, 'body'):
            raise ValueError(f'{case}: complete v4 census required')
        if meta.get('partial') or meta.get('records_total', len(records)) != len(records):
            raise ValueError(f'{case}: incomplete census pages/budget')
        index = {}
        for record in records:
            if not isinstance(record['i'], int) or record['i'] in index:
                raise ValueError(f'{case}: invalid/duplicate record index')
            index[record['i']] = record
            signature = {k: record.get(k) for k in ('k', 'sig', 'pn', 'op')}
            signature['s'] = value_rows(record['s'])
            key = json.dumps(signature, ensure_ascii=False, sort_keys=True)
            groups[key].append((case, record))
        records_by_case[case] = index
        children = collections.defaultdict(set)
        for i, record in index.items():
            if record['k'] in ('box', 'pseudo', 'text', 'media'):
                for parent in record.get('anc', []):
                    if parent in index:
                        children[parent].add(i)
        children_by_case[case] = children
    value_groups = collections.defaultdict(set)
    group_data = []
    for key, members in sorted(groups.items()):
        members.sort(key=lambda item: (item[0], item[1]['i']))
        record = members[0][1]
        gid = 'S-' + hashlib.sha256(key.encode()).hexdigest()[:12]
        rows = []
        for prop, value in value_rows(record['s']):
            cap = {'bgi': 160 if record['k'] == 'pseudo' else 300, 'content': 16, 'mask': 80}.get(prop)
            row = (prop, value, cap is not None and len(value) >= cap)
            rows.append(row)
            value_groups[row].add(gid)
        group_data.append((gid, members, rows))
    value_ids = {row: f'V{index:03d}' for index, row in enumerate(sorted(value_groups), 1)}
    lines = ['# W8 요소 정확값 시트', '',
             '같은 v4 원본 census에서 만든 참고 자료. 원본 소스·시각 연결표와 함께 읽는다.',
             '후보는 관측 직렬화 정밀도에서 일치한다(srgb 6자리, legacy rgb byte). 근접값 허용 오차는 없다.',
             '서체는 첫 서체만 비교한다. 해석 못 한 토큰·잘린 값은 수동 확인하며 자동 등록하지 않는다.',
             '기본값/메타데이터 행은 생략한다. 전체 값·rect·구성원·관계는 원본 census의 case#record로 확인한다.',
             '후보는 속성 종류로 한정하며 6개까지, 관계는 개수와 첫 2개를 표시한다.',
             f'토큰 파일 {"없음" if css is None else "읽음"} · case {len(censuses)} · 모양 묶음 {len(groups)}', '',
             '## 값 → 토큰', '', '| 값 ID | 속성 종류 · 관측 속성 | 값 | 후보 / 처분 | 등장 묶음 |', '|---|---|---|---|---:|']
    for row, vid in value_ids.items():
        prop, value, capped = row
        lines.append(f'| {vid} | {category(prop)} · {inline(prop)} | {inline(value)} | {tokens.lookup(prop, value, capped)} | {len(value_groups[row])} |')
    lines.extend(['', '## 모양 묶음', '',
                  '| 묶음 | 서명 · 종류 | 값 ID | 구성원 | 부모/조상 | 자식 효과 | 관측 한계 |',
                  '|---|---|---|---|---|---|---|'])
    for gid, members, rows in group_data:
        record = members[0][1]
        parents, children = set(), set()
        for c, r in members:
            parents.update(c + '#' + str(i) for i in r.get('anc', []) if i in records_by_case[c])
            children.update(c + '#' + str(i) for i in children_by_case[c].get(r['i'], ()))
        flags = [f'{flag}={sum(bool(r.get(flag)) for _, r in members)}'
                 for flag in ('occ', 'blurocc', 'inf', 'ph') if any(r.get(flag) for _, r in members)]
        if record.get('op', 1) != 1:
            flags.append(f'누적 opacity={record["op"]}')
        lines.append(f'| {gid} | {inline(record["sig"])} {inline(record.get("pn") or record["k"])} | '
                     + ','.join(value_ids[row] for row in rows) + ' | '
                     + sample_refs({c + '#' + str(r['i']) for c, r in members}) + ' | '
                     + sample_refs(parents) + ' | ' + sample_refs(children) + ' | ' + ', '.join(flags) + ' |')
    return '\n'.join(lines) + '\n'


class SheetParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        self.exit(1, f'W8 시트: {message}\n')


def main(argv: list[str] | None = None) -> int:
    parser = SheetParser(description=__doc__)
    parser.add_argument('--census', type=Path, required=True)
    parser.add_argument('--tokens', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        css = args.tokens.read_text() if args.tokens.exists() else None
        result = render_sheet(json.loads(args.census.read_text()), css)
        args.out.write_text(result)
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        print(f'W8 시트 미실행: {exc}', file=sys.stderr)
        return 1
    print('W8 정확값 시트: 생성(참고용·비차단)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
