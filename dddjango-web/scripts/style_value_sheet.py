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
    if re.fullmatch(r'#[0-9a-fA-F]{3,4}|#[0-9a-fA-F]{6}(?:[0-9a-fA-F]{2})?', value):
        digits = value[1:]
        if len(digits) in (3, 4):
            digits = ''.join(ch * 2 for ch in digits)
        channels = tuple(Fraction(int(digits[i:i + 2], 16)) for i in (0, 2, 4))
        alpha = Fraction(int(digits[6:8], 16), 255) if len(digits) == 8 else Fraction(1)
        return ('color', *channels, alpha)
    match = re.fullmatch(r'(rgba?|color)\((.*)\)', value, re.I)
    if not match:
        return {'transparent': ('color', Fraction(0), Fraction(0), Fraction(0), Fraction(0))}.get(value)
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
    return ('color', *channels, alpha)


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
        if match[1].lower() in ('var', 'calc', 'env', 'clamp', 'min', 'max', 'url'):
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
        rows.append((prop, value))
        if prop == 'bd':
            sides = value.split('|')
            if len(sides) == 4:
                for side, part in zip(('top', 'right', 'bottom', 'left'), sides):
                    part = part.strip()
                    rows.append((f'bd.{side}', part))
                    pieces = split_css(part, ' \t')
                    if len(pieces) == 3:
                        rows.extend([(f'bd.{side}.width', pieces[0]), (f'bd.{side}.color', pieces[2])])
        elif prop in ('pad', 'rad', 'gap'):
            pieces = split_css(value, ' \t')
            names = ('row', 'column') if prop == 'gap' else ('top-left', 'top-right', 'bottom-right', 'bottom-left') if prop == 'rad' else ('top', 'right', 'bottom', 'left')
            if len(pieces) == len(names):
                rows.extend((f'{prop}.{name}', part) for name, part in zip(names, pieces))
        elif prop in ('bf', 'fil'):
            match = re.fullmatch(r'blur\(([^()]+)\)', value)
            if match:
                rows.append((prop + '.blur', match[1]))
    return rows


def inline(value: object) -> str:
    return '`' + str(value).replace('`', '&#96;').replace('|', '&#124;').replace('\n', ' ') + '`'


def render_sheet(censuses: dict, css: str | None) -> str:
    values = token_values(css) if css is not None else {}
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
            signature = {k: record.get(k) for k in ('k', 'sig', 'pn', 's', 'op', 'pwh')}
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
    lines = ['# W8 요소 정확값 시트', '',
             '같은 v4 원본 census에서 만든 참고 자료. 원본 소스·시각 연결표와 함께 읽는다.',
             '토큰은 foundation 선언의 정확 일치 후보다. 적용 selector·용도·조합의 판단은 architect가 한다.',
             '근접값 추천·허용 오차 없음. 신규 등록 필요는 자동 작성 지시가 아니며 G1 관문이 아니다.',
             '수동 확인: 문맥 단위(rem/em 등)·계산식·미해결/순환 var·다중 선언은 추측하지 않는다. '
             'v4의 잘린 문자열·가상 요소 측정 한계와 관측 밖 속성은 원본으로 확인한다.',
             f'토큰 파일 {"없음" if css is None else "읽음"} · case {len(censuses)} · 모양 묶음 {len(groups)}', '']
    for key, members in sorted(groups.items()):
        members.sort(key=lambda item: (item[0], item[1]['i']))
        case, record = members[0]
        gid = 'S-' + hashlib.sha256(key.encode()).hexdigest()[:12]
        lines.extend([f'### {gid} · {inline(record["sig"])} {inline(record.get("pn") or record["k"])}', '',
                      f'대표 {inline(case + "#" + str(record["i"]))} · 관측 rect {inline(record.get("r"))} · 누적 opacity {inline(record.get("op"))}',
                      '구성원: ' + ', '.join(inline(c + '#' + str(r['i'])) +
                          (' (' + ', '.join(k for k in ('occ', 'blurocc', 'inf', 'ph') if r.get(k)) + ')'
                           if any(r.get(k) for k in ('occ', 'blurocc', 'inf', 'ph')) else '')
                          for c, r in members)])
        parents, children = set(), set()
        for c, r in members:
            parents.update(c + '#' + str(i) for i in r.get('anc', []) if i in records_by_case[c])
            children.update(c + '#' + str(i) for i in children_by_case[c].get(r['i'], ()))
        lines.extend(['부모/조상: ' + (', '.join(inline(x) for x in sorted(parents)) or '없음'),
                      '자식 효과(census anc 연결): ' + (', '.join(inline(x) for x in sorted(children)) or '없음'), '',
                      '| 관측 속성 | 대표 정확값 | 정확 일치 토큰 후보 |', '|---|---|---|'])
        for prop, value in value_rows(record['s']):
            cap = {'bgi': 160 if record['k'] == 'pseudo' else 300, 'content': 16, 'mask': 80}.get(prop)
            capped = cap is not None and len(value) >= cap
            target = None if capped else canonical(value, prop)
            matches = [name for name, raw in sorted(values.items())
                       if raw is not None and target is not None and canonical(raw, prop) == target]
            if prop in ('lines', 'src') or (prop == 'pos' and value == 'flow'):
                result = '관측 메타데이터(토큰 대상 아님)'
            elif capped:
                result = '신규 등록 필요 · 수동 확인(v4 길이 상한)'
            else:
                result = ', '.join(inline(name) for name in matches) or '신규 등록 필요'
            lines.append(f'| {inline(prop)} | {inline(value)} | {result} |')
        lines.append('')
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
