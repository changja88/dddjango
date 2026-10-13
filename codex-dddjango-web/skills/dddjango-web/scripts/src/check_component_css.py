# 부품 CSS 실림 CS1 — 렌더된 문서 머리 · 기준점의 같은 쌍 · 승인 유입 원인 파일.
# CS 전용 파서다. SH 도우미와 공용 CSS 참조/제품 혼입 의미론은 바꾸지 않는다.
from __future__ import annotations

import posixpath
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .common import (BackstopContext, Finding, _areas, _git_raw, loaded_file, mask_css, mask_html,
                     parent_dir_of)
from .products import (REGISTRY, ProductError, load_products, parsed_tags, products_state,
                       shell_directives)

_TAG = re.compile(r'\{%\s*(\w+)\b(.*?)%\}')  # Django Lexer 와 같은 한 줄 토큰
_TOKENS = re.compile(r'\{%.*?%\}|\{\{.*?\}\}|\{#.*?#\}')
_LITERAL = re.compile(r'''^(["'])([^"'\n]*)\1(?=\s|$)''')
_ASSIGN = re.compile(r'''(?:^|\s)(\w+)=((?:"[^"]*"|'[^']*')(?=\s|$)|\S+)''')
_STATIC_TAG = re.compile(r'''\{%\s*static\s+(["'])([^"'\n]+)\1\s*%\}''')
# 지속 셸 머리가 SH4 로 받는 주소 꼬리 `?v=` 뒤 토큰(check_shell·check_purity 와 같은 꼴) — 같은 파일을 가리키므로 떼고 읽는다.
_SHELL_REV = re.compile(r'\{\{\s*root_state\.shell_rev\s*\}\}')
_SUPER = re.compile(r'\{\{\s*block\.super\b[^}\n]*\}\}')
_SUPER_LITERAL = re.compile(r'\{\{\s*block\.super\s*(?:\|\s*safe\s*)?\}\}')
_CONTROL = {'if': 'endif', 'for': 'endfor', 'ifchanged': 'endifchanged'}
_IMPORT = re.compile(r'''@import\s+(?:url\(\s*(?:(["'])(.*?)\1|([^\s)]+))\s*\)|(["'])(.*?)\4)\s*([^;]*);''', re.I)


def _href(parts: List[Tuple[bool, str]]) -> Tuple[Optional[str], Optional[str]]:
    """href 조각(원문 Django 토큰인가, 글자) → (static 인자, 글자 주소). 원문 토큰이 남아 못 읽으면 (None, None).
    지속 셸 SH4 꼬리 `?v={{ root_state.shell_rev }}` 하나만 떼고 읽는다."""
    parts = list(parts)
    while parts and not parts[-1][0] and not parts[-1][1].strip():
        parts.pop()  # 주소 끝 공백은 브라우저가 뗀다
    rev = (len(parts) >= 2 and parts[-1][0] and _SHELL_REV.fullmatch(parts[-1][1])
           and not parts[-2][0] and parts[-2][1].endswith('?v='))
    if rev:
        parts[-2:] = [(False, parts[-2][1][:-3])]
    text = ''.join(value for _, value in parts).strip()
    real = [i for i, (token, _) in enumerate(parts) if token]
    if not real:
        return None, text
    head = ''.join(value for _, value in parts[:real[0]]).strip()
    tail = ''.join(value for _, value in parts[real[0] + 1:])
    tail = tail if rev else tail.rstrip()  # 떼어 낸 꼬리 앞 공백은 주소 안 글자다
    static = _STATIC_TAG.fullmatch(parts[real[0]][1])
    if len(real) == 1 and not head and static and (not tail or tail[0] in '?#'):
        return static[2], text
    return None, None


def _target(file: str, value: str) -> Optional[str]:
    value = value.strip().lstrip('/')
    if value.startswith(('./', '../')):
        value = posixpath.normpath(posixpath.join(posixpath.dirname(file), value))
    return None if value == '..' or value.startswith('../') else value


@dataclass
class Block:
    name: str
    start: int
    body_start: int
    body_end: int = 0
    end: int = 0
    children: List['Block'] = field(default_factory=list)


class Template:
    def __init__(self, file: str, original: str, error: Optional[str] = None) -> None:
        self.file = file
        self.error = error
        ms = mask_html(original)
        self.text = shell_directives(ms.original, ms.no_comments)
        self.line_of = ms.line_of
        # shell_directives 는 지시문만 가린다. super·href 변수도 verbatim/다른 토큰 안에서는 글자다.
        self.variables: Set[int] = set()
        closing: Optional[str] = None
        for m in _TOKENS.finditer(ms.original):
            token = m.group()
            content = token[2:-2].strip()
            if closing is not None:
                if token.startswith('{%') and content == closing:
                    closing = None
            elif token.startswith('{%') and content[:9] in ('verbatim', 'verbatim '):
                closing = 'end' + content
            elif token.startswith('{{') and self.text[m.start():m.start() + 2] == '{{':
                self.variables.add(m.start())
        self.extends: Optional[Tuple[Optional[str], int]] = None
        self.includes: List[Tuple[int, Optional[str], str, Dict[str, Optional[str]], bool]] = []
        self.blocks: Dict[str, Block] = {}
        self.children: List[Block] = []
        self.controls: List[Tuple[int, int]] = []
        self.scopes: List[Tuple[int, int, Dict[str, Optional[str]]]] = []
        stack: List[Block] = []
        controls: List[Tuple[str, int]] = []
        scopes: List[Tuple[str, int, Dict[str, Optional[str]]]] = []
        for m in _TAG.finditer(self.text):
            kind, arg = m[1], m[2].strip()
            literal = _LITERAL.match(arg)
            if kind == 'extends':
                self.extends = (_target(file, literal[2]) if literal else None, m.start())
            elif kind == 'include':
                value = literal[2] if literal else (arg.split()[0] if arg else '')
                rest = arg[literal.end():] if literal else arg[len(value):]
                # 변수 대입도 이름을 기록한다 — 바깥 글자 대입을 잘못 물려받지 않게 덮는다.
                binds = {a[1]: a[2][1:-1] if _LITERAL.fullmatch(a[2]) else None for a in _ASSIGN.finditer(rest)}
                self.includes.append((m.start(), _target(file, value) if literal else None,
                                      value, binds, bool(re.search(r'\bonly\s*$', rest))))
            elif kind == 'block' and arg:
                b = Block(arg.split()[0], m.start(), m.end())
                (stack[-1].children if stack else self.children).append(b)
                self.blocks[b.name] = b
                stack.append(b)
            elif kind == 'endblock' and stack:
                b = stack.pop()
                b.body_end, b.end = m.start(), m.end()
            if kind in ('with', 'for'):
                if kind == 'with':
                    names = {a[1]: a[2][1:-1] if _LITERAL.fullmatch(a[2]) else None for a in _ASSIGN.finditer(arg)}
                    legacy = re.fullmatch(r'(.+?)\s+as\s+(\w+)', arg)
                    if legacy:
                        literal = _LITERAL.fullmatch(legacy[1])
                        names[legacy[2]] = literal[2] if literal else None
                else:
                    names = {name: None for name in re.findall(r'\w+', arg.split(' in ', 1)[0])}
                    names['forloop'] = None
                scopes.append((kind, m.end(), names))
            elif scopes and kind == 'end' + scopes[-1][0]:
                _, start, names = scopes.pop()
                self.scopes.append((start, m.start(), names))
            if kind in _CONTROL:
                controls.append((kind, m.end()))
            elif controls and kind == _CONTROL[controls[-1][0]]:
                _, start = controls.pop()
                self.controls.append((start, m.start()))
        for b in stack:
            b.body_end = b.end = len(self.text)
        self.scopes.extend((start, len(self.text), names) for _, start, names in scopes)
        self.scopes.sort(key=lambda item: item[0])
        # 속성의 Django 토큰을 같은 길이 안전 글자로 가렸다 복원한다(위치·줄 보존).
        tokens: Dict[str, str] = {}
        def hide(m: re.Match) -> str:
            token = ('C%x' % len(tokens)).ljust(len(m.group()), '_')
            tokens[token] = m.group()
            return token
        reading = _TOKENS.sub(hide, self.text)
        tags = parsed_tags(reading)
        if tags is None:
            self.error = self.error or 'HTML 판독 불가'
        self.tags = tags or []
        restore = re.compile('|'.join(map(re.escape, tokens))) if tokens else None
        # 속성마다 (원문 Django 토큰인가, 글자) 조각을 남긴다 — HTML 기호(&#123; 등)를 풀어 생긴 글자는 토큰이 아니다.
        self.parts: Dict[int, Dict[str, List[Tuple[bool, str]]]] = {}
        for tag in self.tags:
            parts: Dict[str, List[Tuple[bool, str]]] = {}
            for name, value in tag.attrs.items():
                pieces, pos = [], 0
                for m in (restore.finditer(value) if value and restore else ()):
                    pieces += [(False, value[pos:m.start()]), (True, tokens[m.group()])]
                    pos = m.end()
                parts[name] = [piece for piece in pieces + [(False, (value or '')[pos:])] if piece[1]]
            self.parts[tag.start] = parts
            if restore:
                tag.attrs = {name: restore.sub(lambda m: tokens[m.group()], value) if value else value
                             for name, value in tag.attrs.items()}
        self.heads = [t for t in self.tags if t.name == 'head']

    def scope(self, offset: int, binds: Dict[str, str]) -> Dict[str, Optional[str]]:
        values: Dict[str, Optional[str]] = dict(binds)
        for a, b, names in self.scopes:
            if a <= offset < b:
                values.update(names)
        return values

    def inactive(self, offset: int) -> bool:
        return any(t.name in ('template', 'noscript') and t.open_end <= offset < t.close_start for t in self.tags)

    def in_head(self, offset: int, override: Optional[bool]) -> bool:
        return override if override is not None else any(t.open_end <= offset < t.close_start for t in self.heads)

    def conditional(self, offset: int) -> bool:
        return any(a <= offset < b for a, b in self.controls)


# 키에 줄 번호를 싣지 않는다 — 줄 이동은 새 미검증이 아니고 부모 측정의 위반 키도 안정적이다.
UnverifiedKey = Tuple[str, str, str]


@dataclass
class Analysis:
    has_head: bool = False
    rendered: Set[str] = field(default_factory=set)
    dependencies: Set[str] = field(default_factory=lambda: {REGISTRY})
    existence: Set[str] = field(default_factory=set)  # 필요 CSS 후보는 존재 여부만 판정 입력이다.
    linked: Set[str] = field(default_factory=set)  # link와 import 닫힘은 파일 내용도 판정 입력이다.
    need: Dict[str, str] = field(default_factory=dict)  # CSS → 들어온 길
    loaded: Set[str] = field(default_factory=set)
    conditional: Dict[str, Tuple[str, int]] = field(default_factory=dict)
    body: Dict[str, str] = field(default_factory=dict)
    dead: Set[str] = field(default_factory=set)
    missing_own: Set[str] = field(default_factory=set)
    unreadable: Dict[UnverifiedKey, str] = field(default_factory=dict)
    uncertain_reads: bool = False
    product: Optional[str] = None


class Tree:
    """현재/기준점 읽기 뷰. 기준점은 변경 파일과 링크·대상을 git show 로 읽는다."""
    def __init__(self, ctx: BackstopContext, baseline: bool = False) -> None:
        self.ctx = ctx
        self.baseline = baseline
        self.base_files = ctx.base_files
        if ctx.gated:
            cached = getattr(ctx, '_component_css_base_files', None)
            if cached is None:
                prefix = (_git_raw(ctx.root, ['rev-parse', '--show-prefix']) or '').rstrip('\n') + 'web/'
                listing = _git_raw(ctx.root, ['ls-tree', '--full-tree', '-r', '--name-only', '-z', ctx.diff_base])
                cached = {f[len(prefix):] for f in (listing or '').split('\x00') if f.startswith(prefix)}
                setattr(ctx, '_component_css_base_files', cached)
                setattr(ctx, '_component_css_listing_failed', listing is None)
            self.base_files = cached
        self.files = self.base_files if baseline else ctx.files_set
        self.changed = ctx.touched | (self.base_files - ctx.files_set)
        self.existence_changed = (set() if getattr(ctx, '_component_css_listing_failed', False)
                                  else self.files ^ self.base_files)
        self.content_changed = self.changed if baseline or not ctx.gated else self._content_changes()
        self.templates: Dict[str, Template] = {}
        self.css: Dict[str, Optional[str]] = {}  # 같은 Tree의 CSS 읽기 결과를 문서 사이에 공유한다.
        self.read_errors: Dict[str, str] = {}
        self.read_dependencies: Dict[str, Set[str]] = {}
        self.symlinks: Set[str] = set()
        self.symlink_listing_failed = False
        if baseline:
            prefix = (_git_raw(ctx.root, ['rev-parse', '--show-prefix']) or '').rstrip('\n') + 'web/'
            listing = _git_raw(ctx.root, ['ls-tree', '--full-tree', '-r', '-z', ctx.diff_base])
            self.symlink_listing_failed = listing is None
            self.symlinks = {entry.split('\t', 1)[1][len(prefix):] for entry in (listing or '').split('\x00')
                             if entry.startswith('120000 ') and '\t' in entry
                             and entry.split('\t', 1)[1].startswith(prefix)}
        self.products = products_state(ctx)
        dirs = {parent.as_posix() for f in self.files for parent in Path(f).parents if parent.as_posix() != '.'}
        self.areas = _areas(sorted(self.files), dirs) if baseline else ctx.areas
        if baseline and REGISTRY in self.changed:
            # 기존 제품 검증을 재사용한다. 기준점 선언 오류면 기준점 결과 전체를 없음으로 본다.
            with tempfile.TemporaryDirectory(prefix='web-cs-products-') as tmp:
                root = Path(tmp)
                if REGISTRY in self.files:
                    text = self.read(REGISTRY)
                    if text is None:
                        raise ProductError('기준점 제품 선언 못 읽음')
                    (root / 'web').mkdir()
                    (root / 'web' / REGISTRY).write_text(text, encoding='utf-8')
                self.products = load_products(root)

    def _content_changes(self) -> Set[str]:
        if not self.changed:
            return set()
        # 내용 0/0인 권한 변경은 입력이 같다. T는 링크 해소 결과가 달라질 수 있다.
        tokens = (_git_raw(self.ctx.root, ['diff', '--relative', '--no-renames', '--raw', '--numstat',
                                         '-z', self.ctx.diff_base]) or '').split('\x00')
        same = {t.split('\t', 2)[2][4:] for t in tokens if t.startswith('0\t0\tweb/')}
        old_exists = set()
        for i, token in enumerate(tokens[:-1]):
            if not token.startswith(':') or not tokens[i + 1].startswith('web/'):
                continue
            file = tokens[i + 1][4:]
            fields = token[1:].split()
            if fields[0] != '000000':
                old_exists.add(file)
            if fields[-1] == 'T':
                same.discard(file)
            elif fields[-1] == 'D' and file in self.files:
                # index에서 빠졌어도 현물은 남을 수 있다 — 이 경우만 실제 바이트를 대조한다.
                same.discard(file)
                path = self.ctx.web / file
                symlink = path.is_symlink()
                if (fields[0] == '120000') != symlink:
                    continue
                try:
                    content = os.fsencode(os.readlink(path)) if symlink else path.read_bytes()
                    old = subprocess.run(['git', '-C', str(self.ctx.root), 'show',
                                          '%s:./web/%s' % (self.ctx.diff_base, file)], capture_output=True)
                except OSError:
                    continue
                if old.returncode == 0 and old.stdout == content:
                    same.add(file)
        if getattr(self.ctx, '_component_css_listing_failed', False):
            # 못 읽은 목록을 빈 기준점으로 삼지 않는다. Git diff로 아는 생성·삭제만 센다.
            self.existence_changed.update((old_exists - self.files) | (self.ctx.added - old_exists))
            same &= self.files & old_exists
        else:
            same &= self.files & self.base_files
        return self.changed - same

    def read(self, file: str, seen: Optional[Set[str]] = None, through_link: bool = False) -> Optional[str]:
        if file not in self.files:
            return None  # 목록 밖은 부재다. 기준점 판독 실패로 만들지 않는다.
        if self.symlink_listing_failed:
            self.read_errors[file] = 'git ls-tree 링크 형식 판독 실패'
            return None
        seen = set() if seen is None else seen
        if file in seen:
            self.read_errors[file] = '심볼릭 링크 순환'
            return None
        seen.add(file)
        path = self.ctx.web / file
        try:
            symlink = file in self.symlinks if self.baseline else path.is_symlink()
            if self.baseline and (file in self.changed or symlink or through_link):
                text = _git_raw(self.ctx.root, ['show', '%s:./web/%s' % (self.ctx.diff_base, file)])
                if text is None:
                    self.read_errors[file] = 'git show 실패'
                    return None
                if '\ufffd' in text:
                    # 공용 git 읽기의 대체 글자가 실제 UTF-8 글자인지 CS 에서만 확인한다.
                    raw = subprocess.run(['git', '-C', str(self.ctx.root), 'show',
                                          '%s:./web/%s' % (self.ctx.diff_base, file)], capture_output=True)
                    if raw.returncode:
                        self.read_errors[file] = 'git show 실패'
                        return None
                    text = raw.stdout.decode('utf-8')
            else:
                text = os.readlink(path) if symlink else path.read_text(encoding='utf-8')
            if not symlink:
                return text
            target = posixpath.normpath(posixpath.join(posixpath.dirname(file), text))
            if target.startswith('/') or target == '..' or target.startswith('../'):
                self.read_errors[file] = 'web 뿌리 밖 심볼릭 링크'
                return None
            content = self.read(target, seen, True)
            self.read_dependencies[file] = {target} | self.read_dependencies.get(target, set())
            if content is None and target in self.files:
                self.read_errors[file] = '심볼릭 링크 대상 판독 불가'
            return content
        except (OSError, UnicodeError) as error:
            self.read_errors[file] = type(error).__name__
            return None

    def template(self, file: str) -> Template:
        if file not in self.templates:
            text = self.read(file)
            self.templates[file] = Template(file, text or '', self.read_errors.get(file))
        return self.templates[file]

    def chain(self, file: str) -> List[Template]:
        chain, seen = [], set()
        while file in self.files and file not in seen:
            seen.add(file)
            t = self.template(file)
            chain.append(t)
            if t.extends is None or t.extends[0] is None:
                break
            file = t.extends[0]
        return chain

    def imports(self, file: str, dependencies: Set[str], seen: Set[str]) -> None:
        dependencies.add(file)
        if file in seen or file not in self.files:
            return
        if file not in self.css:
            self.css[file] = self.read(file)
        content = self.css[file]
        dependencies.update(self.read_dependencies.get(file, set()))
        if content is None:
            return
        seen.add(file)
        text = mask_css(content).no_comments.split('{', 1)[0]
        served = '/static/web/' + file[7:] if file.startswith('static/') else '/static/' + file
        for m in _IMPORT.finditer(text):
            if m[6].strip().lower() not in ('', 'all', 'screen'):
                continue
            target = loaded_file(m[2] or m[3] or m[5], posixpath.dirname(served))
            if target and target.endswith('.css'):
                self.imports(target, dependencies, seen)

    def analyse(self, file: str) -> Analysis:
        result = Analysis(product=self.products.product_of(file, self.areas))
        root_chain = self.chain(file)
        if file.startswith('root/') and result.product is None:
            result.product = next((self.products.product_of_shell(t.file) for t in root_chain
                                   if t.file in self.products.shells), None)
        visited: Set[Tuple[str, Tuple[Tuple[str, str], ...], Optional[bool], bool, bool]] = set()

        def unreadable(t: Template, offset: int, why: str, slot: Optional[str] = None) -> None:
            directive = _TAG.match(t.text, offset)
            if slot is None:
                slot = directive[1] + ' ' + directive[2].strip() if directive else why
            receiving = '' if file == t.file else 'web/%s ← ' % file
            result.unreadable[('못 읽음', file, t.file + ' ' + slot)] = '[info] CS1 미검증(못 읽음) — %sweb/%s:%d · %s' % (
                receiving, t.file, t.line_of(offset), why)

        def need(t: Template, via: str) -> None:
            if not self.products.in_component(t.file) or not t.file.endswith('.html'):
                return
            relative = '/'.join(self.products.ds_rel(t.file))[:-5] + '.css'
            css = self.products.ds_root(result.product) + '/' + relative
            flat = 'design_system/' + relative
            result.dependencies.update((css, flat))  # 파일이 새로 생기는 경우도 판정에 쓰인다.
            result.existence.update((css, flat))
            if css in self.files or (result.product in self.products.own and flat in self.files):
                result.need.setdefault(css, via + ' → ' + t.file)
                if css not in self.files:
                    result.missing_own.add(css)

        def walk(source: str, binds: Dict[str, str], head: Optional[bool], conditional: bool, via: str,
                 inactive: bool = False) -> None:
            result.dependencies.add(source)
            key = (source, tuple(sorted(binds.items())), head, conditional, inactive)
            if key in visited:
                return
            visited.add(key)
            chain = self.chain(source)
            if not chain:
                t = self.template(source)
                unreadable(t, 0, '템플릿이 파일 목록에 없음')
            for t in chain:
                result.rendered.add(t.file)
                result.dependencies.add(t.file)
                result.dependencies.update(self.read_dependencies.get(t.file, set()))
                if t.error:
                    prefix = '기준점 ' if self.baseline else ''
                    reason = prefix + ('HTML 판독 불가' if t.error == 'HTML 판독 불가'
                                       else '파일 판독 불가(%s)' % t.error)
                    unreadable(t, 0, reason, reason)
                    result.uncertain_reads = True
                need(t, via)
                if t.extends:
                    if t.extends[0] is None:
                        unreadable(t, t.extends[1], '변수 extends')
                    else:
                        result.dependencies.add(t.extends[0])
                        if t.extends[0] not in self.files:
                            unreadable(t, t.extends[1], '상속 대상이 파일 목록에 없음')

            def segment(t: Template, a: int, b: int, flag: Optional[bool], cond: bool, inert: bool) -> None:
                events = [(tag.start, 'tag', tag) for tag in t.tags if a <= tag.start < b]
                events += [(inc[0], 'include', inc) for inc in t.includes if a <= inc[0] < b]
                for offset, kind, item in sorted(events, key=lambda event: event[0]):
                    if kind == 'include':
                        _, literal, value, assignments, only = item
                        at_scope = t.scope(offset, binds)
                        resolved = at_scope.get(value)
                        target = literal or (_target(t.file, resolved) if resolved is not None else None)
                        if target is None:
                            unreadable(t, offset, '변수 include `%s`' % value)
                            continue
                        scope = {} if only else {name: value for name, value in at_scope.items() if value is not None}
                        for name, assigned in assignments.items():
                            scope.pop(name, None)
                            if assigned is not None and assigned.endswith('.html'):
                                scope[name] = assigned
                        child_head = True if t.in_head(offset, flag) else (
                            False if flag is not None or t.heads else None)
                        walk(target, scope, child_head, cond or t.conditional(offset),
                             '%s:%d' % (t.file, t.line_of(offset)), inert or t.inactive(offset))
                        continue
                    tag = item
                    if tag.name == 'head':
                        result.has_head = True
                    if tag.name != 'link':
                        continue
                    rel = (tag.attrs.get('rel') or '').lower().split()
                    parts = t.parts.get(tag.start, {})
                    dynamic = {name for name in ('rel', 'media', 'disabled') if any(real for real, _ in parts.get(name, ()))}
                    static, href = _href(parts.get('href', []))
                    if href is None:
                        dynamic.add('href')
                    if 'rel' not in dynamic and 'stylesheet' not in rel:
                        continue  # CSS 아닌 link(canonical · icon · preconnect …)는 주소가 동적이어도 부품 CSS 와 무관하다.
                    media = (tag.attrs.get('media') or '').strip().lower()
                    dead = (inert or t.inactive(tag.start) or ('rel' not in dynamic and 'alternate' in rel)
                            or ('disabled' not in dynamic and 'disabled' in tag.attrs)
                            or ('media' not in dynamic and media not in ('', 'all', 'screen')))
                    if dynamic:
                        if t.in_head(tag.start, flag) and not dead:
                            unreadable(t, tag.start, '동적 link 주소', 'link ' + repr(tag.attrs))
                        continue
                    if static is None and not href.startswith('/'):
                        continue  # 맨 앞 `/` 없는 글자 주소는 페이지 주소 기준으로 풀린다 — 정적 파일이 아니다.
                    css = loaded_file(static if static is not None else href)
                    if css is None:
                        continue
                    result.dependencies.add(css)
                    loaded = result.loaded if not (dead or not t.in_head(tag.start, flag)
                                                    or cond or t.conditional(tag.start)) else set()
                    self.imports(css, result.linked, loaded)
                    if dead:
                        if not (inert or t.inactive(tag.start)):
                            result.dead.add(css)
                    elif not t.in_head(tag.start, flag):
                        result.body.setdefault(css, t.file)
                    elif cond or t.conditional(tag.start):
                        result.conditional.setdefault(css, (t.file, t.line_of(tag.start)))

            # 맨 위 템플릿의 block 자리에서 가장 아래 정의를 렌더한다. super 는 그 토큰 자리에 바로 위 정의를 넣는다.
            active: Set[Tuple[str, int]] = set()

            def block(name: str, flag: Optional[bool], cond: bool, inert: bool, depth: int = 0) -> None:
                definitions = [(t, t.blocks[name]) for t in chain if name in t.blocks]
                if depth >= len(definitions) or (name, depth) in active:
                    return
                active.add((name, depth))
                t, b = definitions[depth]
                region(t, b.body_start, b.body_end, b.children, flag, cond, inert, (name, depth + 1))
                active.remove((name, depth))

            def region(t: Template, a: int, b: int, children: List[Block], flag: Optional[bool],
                       cond: bool, inert: bool, parent: Optional[Tuple[str, int]] = None) -> None:
                events = [(c.start, c.end, c) for c in children if a <= c.start < b]
                events += [(m.start(), m.end(), None) for m in _SUPER.finditer(t.text, a, b)
                           if m.start() in t.variables
                           and not any(c.start <= m.start() < c.end for c in children)] if parent else []
                pos = a
                for start, end, child in sorted(events, key=lambda item: item[0]):
                    segment(t, pos, start, flag, cond, inert)
                    child_flag = flag if flag is not None else (t.in_head(start, None) if t.heads else None)
                    child_cond = cond or t.conditional(start)
                    child_inert = inert or t.inactive(start)
                    if child is None and parent:
                        filtered = not _SUPER_LITERAL.fullmatch(t.text[start:end])
                        if filtered and t.in_head(start, child_flag) and not child_inert:
                            unreadable(t, start, 'block.super 필터 판독 불가', t.text[start:end])
                        # 필터가 글자를 바꿔도 부모 block 의 부품은 렌더될 수 있다 — 요구는 세고 그 안 link 는 실림이 아니다.
                        block(parent[0], child_flag, child_cond, child_inert or filtered, parent[1])
                    elif child is not None:
                        block(child.name, child_flag, child_cond, child_inert)
                    pos = end
                segment(t, pos, b, flag, cond, inert)

            if chain:
                top = chain[-1]
                region(top, 0, len(top.text), top.children, head, conditional, inactive)

        walk(file, {}, None, False, file + ':1')
        result.dependencies.update(result.linked)
        for source in sorted(result.dependencies & self.read_errors.keys()):
            if source not in self.files:
                continue
            prefix = '기준점 ' if self.baseline else ''
            reason = prefix + '파일 판독 불가(%s)' % self.read_errors[source]
            unreadable(self.template(source), 0, reason, reason)
            result.uncertain_reads = True
        return result


@dataclass
class Results:
    analyses: Dict[str, Analysis] = field(default_factory=dict)
    missing: Dict[Tuple[str, str], Analysis] = field(default_factory=dict)
    unverified: Dict[UnverifiedKey, str] = field(default_factory=dict)
    owners: Dict[UnverifiedKey, Set[str]] = field(default_factory=dict)


def _calculate(tree: Tree) -> Results:
    result = Results()
    html = sorted(f for f in tree.files if f.endswith('.html'))
    extended = {t.extends[0] for t in (tree.template(f) for f in html) if t.extends}
    candidates = [f for f in html if not f.startswith('design_system/') and f not in tree.products.shells
                  and (parent_dir_of(f) == 'view' or f not in extended)]
    for file in candidates:
        result.analyses[file] = tree.analyse(file)
    documents = {f for f, a in result.analyses.items() if a.has_head}
    inner = {r for f, a in result.analyses.items() for r in a.rendered if r != f}
    roots = set(candidates) - documents - inner

    def unverified(key: UnverifiedKey, message: str, owner: str) -> None:
        result.unverified.setdefault(key, message)
        result.owners.setdefault(key, set()).add(owner)

    for file, a in result.analyses.items():
        if file in documents:
            for css in sorted(a.need):
                if css in a.loaded and css not in a.missing_own:
                    continue
                if css in a.conditional and css not in a.missing_own:
                    source, line = a.conditional[css]
                    unverified(('조건부', file, css), '[info] CS1 미검증(조건부) — web/%s: %s(web/%s:%d 의 link 가 조건 안에 있다)'
                               % (file, css, source, line), file)
                else:
                    result.missing[file, css] = a
        elif file in roots and a.need:
            # 내부 키는 쌍마다, 표시는 조각 뿌리마다 한 줄이다(기준점과 CSS 이동도 쌍으로 비교).
            for css in sorted(a.need):
                unverified(('조각', file, css), '', file)
        if file in documents or file in roots:
            for key, message in a.unreadable.items():
                unverified(key, message, file)
    return result


def _moves(ctx: BackstopContext, design_build: Optional[str], base_files: Set[str]) -> Dict[str, str]:
    from .debt import DebtError, parse_spec_pairs
    # CS 전용 개명 읽기 — 공용 touched/added 의미론은 그대로 둔다.
    prefix = (_git_raw(ctx.root, ['rev-parse', '--show-prefix']) or '').rstrip('\n') + 'web/'
    tokens = (_git_raw(ctx.root, ['diff', '-M100%', '--name-status', '-z', ctx.diff_base]) or '').split('\x00')
    pairs = []
    i = 0
    while i < len(tokens) - 1:
        status = tokens[i]
        if status.startswith(('R', 'C')) and i + 2 < len(tokens):
            old, new = tokens[i + 1:i + 3]
            if status == 'R100' and old.startswith(prefix) and new.startswith(prefix):
                pairs.append((old[len(prefix):], new[len(prefix):]))
            i += 3
        else:
            i += 2
    if design_build:
        path = Path(design_build) / 'design-spec.md'
        if path.is_file():
            try:
                pairs.extend(parse_spec_pairs(path.read_text(encoding='utf-8'))[0])
            except (DebtError, OSError, UnicodeError) as error:
                ctx.notices.append('[info] CS1 이동 대응 생략 — 명세 슬라이스 0 절 판독 불가(%s)' % error)
    moves: Dict[str, str] = {}
    for old, new in pairs:
        for source in sorted(base_files):
            dest = new + source[len(old):] if old.endswith('/') and source.startswith(old) else new if source == old else None
            if (dest is not None and source not in ctx.files_set and dest in ctx.files_set and dest not in base_files):
                moves.setdefault(source, dest)
    return moves


def run_component_css(ctx: BackstopContext, design_build: Optional[str] = None) -> List[Finding]:
    current_tree = Tree(ctx)
    current = _calculate(current_tree)
    before = Results()
    moves: Dict[str, str] = {}
    if ctx.gated:
        moves = _moves(ctx, design_build, current_tree.base_files)
        try:
            before = _calculate(Tree(ctx, True))
        except ProductError:
            pass  # 기준점 선언을 못 읽으면 현재 결과는 모두 새 것이다.
    old_missing = {(moves.get(f, f), moves.get(c, c)) for (f, c), a in before.missing.items() if not a.uncertain_reads}
    def moved_key(key: UnverifiedKey) -> UnverifiedKey:
        kind, receiving, value = key
        if kind == '못 읽음':
            source, _, directive = value.partition(' ')
            value = moves.get(source, source) + ' ' + directive
        else:
            value = moves.get(value, value)
        return kind, moves.get(receiving, receiving), value
    # 판독 실패는 기준점의 렌더 사실이 아니다. 현재의 진단 키로 올려 같은 차집합으로 보고한다.
    for key, message in before.unverified.items():
        if ' · 기준점 ' in message:
            for old, new in moves.items():
                message = message.replace('web/' + old + ':', 'web/' + new + ':')
                message = message.replace('web/' + old + ' ←', 'web/' + new + ' ←')
            current.unverified.setdefault(moved_key(key), message)
    if getattr(ctx, '_component_css_listing_failed', False):
        for file, a in current.analyses.items():
            if a.has_head or a.need or a.unreadable:
                reason = '기준점 파일 목록 판독 불가'
                current.unverified[('못 읽음', file, file + ' ' + reason)] = (
                    '[info] CS1 미검증(못 읽음) — web/%s:1 · %s' % (file, reason))
    old_unverified = {moved_key(key) for key, message in before.unverified.items() if ' · 기준점 ' not in message}
    old_dependencies: Dict[str, Set[str]] = {}
    for file, a in before.analyses.items():
        old_dependencies.setdefault(moves.get(file, file), set()).update(a.dependencies)

    def dependencies(file: str) -> Set[str]:
        return current.analyses[file].dependencies | old_dependencies.get(file, set())

    changed = current_tree.changed
    considered = {f for f in current.analyses if not ctx.gated or dependencies(f) & changed}
    # BLOCKER는 판정 입력이 같은 문서를 건너뛴다. 미검증은 아래에서 키만 비교한다.
    judged = set(current.analyses) if not ctx.gated else set()
    # 제품 소속(area 판별 · 선언)이 바뀌면 필요 CSS 의 뿌리도 바뀐다 — 파일 변경이 없어도(빈 폴더) 다시 판정한다.
    # 기준점 판독 실패로 제품을 못 정한 문서는 비교하지 않는다(같은 입력 보호).
    moved_product = {f for f, a in current.analyses.items() if ctx.gated and f in before.analyses
                     and not (before.analyses[f].uncertain_reads and before.analyses[f].product is None)
                     and before.analyses[f].product != a.product}
    judged |= moved_product
    if ctx.gated and (current_tree.content_changed or current_tree.existence_changed):
        for file, a in current.analyses.items():
            old = before.analyses.get(file, Analysis())
            existence = a.existence | old.existence
            content = dependencies(file) - (existence - a.linked - old.linked)
            if content & current_tree.content_changed:
                judged.add(file)
            elif current_tree.existence_changed:
                needed = set(a.need) | set(old.need)
                needed.update('design_system/' + c.split('/', 2)[2] for c in a.missing_own | old.missing_own)
                if needed & current_tree.existence_changed:
                    judged.add(file)
    notices = []
    fragments: Dict[str, List[str]] = {}
    for key, message in sorted(current.unverified.items()):
        if key in old_unverified:
            continue
        kind, file, css = key
        if kind == '조각':
            fragments.setdefault(file, []).append(css)
        else:
            notices.append(message)
    notices += ['[info] CS1 미검증(조각) — web/%s: %s(받는 문서를 정적으로 알 수 없다)' % (f, ' · '.join(css))
                for f, css in sorted(fragments.items())]
    ctx.notices.extend(notices)
    if notices:
        ctx.notices.append('[info] CS1 미검증 %d건 — 통과가 아니다: 감수 확인 뒤 G2 배너와 마무리 보고에 남긴다' % len(notices))
    existing: Dict[str, List[str]] = {}
    findings = []
    for (file, css), a in sorted(current.missing.items()):
        if (file, css) in old_missing:
            if file in considered:
                existing.setdefault(file, []).append(css)
            continue
        if file not in judged:
            continue
        message = '부품 CSS 가 이 문서에 실리지 않는다'
        if css in a.missing_own:
            message = '제품 %s 뿌리에 이 부품 CSS 가 없다 — %s(평면 것은 다른 제품 몫)' % (a.product, css)
        else:
            if css in a.body:
                message += '(본문 %s 에서만 실린다 — 머리로 옮긴다)' % a.body[css]
            elif css in a.dead:
                message += '(인쇄 전용 · disabled · alternate link 뿐)'
            message += ' — ' + css
        tpl = current_tree.template(file)
        line = tpl.line_of(tpl.extends[1]) if tpl.extends else 1
        static = 'web/' + css[7:] if css.startswith('static/') else css
        fix = ('이 문서 머리에 한 줄 싣는다 — <link rel="stylesheet" href="{% static \'' + static + '\' %}">'
               ' · 자리 = 페이지 {% block head %}(셸의 모든 화면이 쓰면 셸 <head> · 지속 셸은 셸 <head> 에 ?v= 꼬리와 함께)'
               ' · 들어온 길: ' + a.need[css])
        if css in a.missing_own:
            fix = '제품 %s 부품 CSS 를 먼저 작성한다 — web/%s · 작성 뒤 이 문서 머리에 싣는다 · 들어온 길: %s' % (
                a.product, css, a.need[css])
        causes = dependencies(file) & changed
        if file in moved_product and not causes:  # 제품 소속만 바뀐 문서 — area 를 가른 생성·삭제가 원인이다(승인 유입 가름)
            area = '/'.join(file.split('/')[:2]) + '/'
            causes |= {f for f in current_tree.existence_changed if f.startswith(area)}
        causes = tuple('web/' + f for f in sorted(causes)) if ctx.gated else ()
        findings.append(Finding('CS1', file, line, message, 'implementation-django §10 부품 CSS', fix, causes=causes))
    for file, css in sorted(existing.items()):
        ctx.notices.append('[info] CS1 기존 누락 — web/%s: %s … %d종(기준점에서 이미 빠져 있었다 · 명세 «부품 CSS 표» 가 처분)'
                           % (file, ' · '.join(css), len(css)))
    return findings
