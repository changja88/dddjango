# WV — 공식 플랫폼 SDK 등재 13종 (값 정본: discipline-houserules §9).
# 대상별 의미론(§9 «늘 검사의 대상»):
#   목록 파일          WV1 형식 · WV3 결속·출처 · WV4 공식성          — 늘(게이트 무관 · 미룰 수 없음)
#   등재 id 디렉터리    WV2 사본 바이트 · WV5 정확성·표지 · WV6 참조     — 늘
#   목록 시대 미등재    WV13 강등 금지                                 — 늘(목록 유무 무관)
#   목록 시대 전 미등재 WV12 이관 항목                                 — 빚 스캔만(미룰 수 있음)
#   기능 JS·템플릿     WV7 공개 키 리터럴 · WV9 사용 범위(목록) · WV8 외부 코드·주소(모든 경우) — added 줄
#   빌드 기록 범위      WV10 SDK 변경 격리                             — gated(빌드 기록이 있을 때)
#   빚 스캔            WV11 미사용 SDK
#
# *왜 결정적 백스톱인가*: 등재 사본·목록·참조는 바이트·경로·이력의 사실이고, 기능 JS 의 외부 코드 끌어오기·
# 외부 주소·범위 밖 호출은 리터럴·토큰 꼴의 덫이다(남는 몫은 리뷰어와 G2 실행 확인이 받는다).
# (바탕: dddjango-web v1.3.1 src/check_vendor.py — 번호·의미 그대로. 등재 상태는 `sdk_state(ctx)` 로 받는다)

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .common import VERBATIM_RE, BackstopContext, Finding
from .sdk_registry import (HOSTING_SUFFIXES, SDK_REGISTRY, VENDOR_ATTRS, VENDOR_ATTRS_BYTES, VENDOR_DIR,
                           RegistryError, SdkState, approval_problems, canonical_bytes, is_os_junk_name,
                           lib_cdn_reason, normalize_gateway_url, parse_scope_item, sdk_state, service_hosts,
                           trap_hits, validate_registry)

VENDOR_CHECK_IDS: Tuple[str, ...] = tuple('WV%d' % n for n in range(1, 14))
UNDEFERRABLE: Set[str] = {'WV1', 'WV2', 'WV3', 'WV4', 'WV5', 'WV6', 'WV13'}
_RULE: str = 'discipline-houserules §9 공식 SDK'
SDK_TITLE: str = 'chore(web-sdk):'
_REG_ENTRY: str = '이 요청이 그 단위·그 사본을 부르는 화면에 닿으면 슬라이스 0 «기존 등록»(G1 SDK 문항)'


class VendorUndecidable(Exception):
    """판정 불가 — 백스톱 계약상 exit 1(미실행 · 통과가 아니다)."""


def _f(check: str, path: str, line: Optional[int], message: str, fix: str) -> Finding:
    return Finding(check, path, line, message, _RULE, fix)


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(['git', '-C', str(root), *args], capture_output=True)


def _git_text(root: Path, *args: str) -> str:
    r = _git(root, *args)
    return r.stdout.decode('utf-8', 'surrogateescape') if r.returncode == 0 else ''


def _repo_prefix(root: Path) -> Optional[str]:
    r = _git(root, 'rev-parse', '--show-prefix')
    return r.stdout.decode('utf-8', 'surrogateescape').strip() if r.returncode == 0 else None


# ------------------------------------------------------------------ JS 리터럴 · 코드 뷰


_NS_URIS: Set[str] = {'http://www.w3.org/2000/svg', 'http://www.w3.org/1999/xlink', 'http://www.w3.org/1999/xhtml',
                      'http://www.w3.org/1998/Math/MathML', 'http://www.w3.org/XML/1998/namespace',
                      'http://www.w3.org/2000/xmlns/'}
_STRONG_TLD: Set[str] = {'com', 'net', 'org', 'kr', 'jp', 'cn'}
_WEAK_TLD: Set[str] = {'io', 'dev', 'app', 'co', 'me', 'xyz', 'cloud'}
_PH: str = '\ue000'
_ESC = re.compile(r'\\(?:x[0-9a-fA-F]{2}|u\{[0-9a-fA-F]+\}|u[0-9a-fA-F]{4}|[0-7]{1,3}|.)', re.S)
_DOMAIN = re.compile(r'(?<![a-z0-9.\-])([a-z0-9-]+(?:\.[a-z0-9-]+)*)\.(com|net|org|io|dev|app|co|kr|jp|cn|me|xyz|cloud)'
                     r'(?![a-z0-9-])', re.I)
_SCHEME = re.compile(r'^\s*(https?|wss?):', re.I)
_REGEX_PREV: str = '(,=:[!&|?{};+-*%<>~^'
_REGEX_WORDS: Set[str] = {'return', 'typeof', 'instanceof', 'in', 'of', 'new', 'delete', 'void', 'throw', 'case',
                          'do', 'else', 'yield', 'await'}


def _decode(body: str) -> str:
    def rep(m: 're.Match[str]') -> str:
        e: str = m.group(0)
        if e.startswith('\\x'):
            return chr(int(e[2:], 16))
        if e.startswith('\\u{'):
            return chr(int(e[3:-1], 16))
        if e.startswith('\\u'):
            return chr(int(e[2:], 16))
        if e[1:].isdigit() and all(c in '01234567' for c in e[1:]):
            return chr(int(e[1:], 8))
        return {'n': '\n', 't': '\t', 'r': '\r', 'b': '\b', 'f': '\f', 'v': '\v'}.get(e[1], e[1])
    return _ESC.sub(rep, body)


class JsView:
    """주석을 지운 JS 의 리터럴 목록과 코드 뷰(리터럴 글자는 공백 — `${…}` 식은 코드로 남는다).
    literals = [(시작 offset, 끝 offset, 따옴표, 값)] — 템플릿의 `${…}` 는 자리표시 한 글자로 값에 든다."""

    def __init__(self, text: str) -> None:
        self.text: str = text
        self.code: List[str] = list(text)
        self.literals: List[Tuple[int, int, str, str]] = []
        self._starts: Optional[Dict[int, Tuple[int, int, str, str]]] = None
        self._scan(0, len(text), top=True)
        self.code_text: str = ''.join(self.code)

    def _blank(self, a: int, b: int) -> None:
        for k in range(a, b):
            if self.code[k] != '\n':
                self.code[k] = ' '

    def _string(self, i: int) -> int:
        t: str = self.text
        q: str = t[i]
        j: int = i + 1
        while j < len(t):
            if t[j] == '\\':
                j += 2
                continue
            if t[j] == q or t[j] == '\n':
                break
            j += 1
        end: int = min(j + 1, len(t)) if j < len(t) and t[j] == q else j
        self.literals.append((i, end, q, _decode(t[i + 1:j])))
        self._blank(i + 1, j)
        return end

    def _template(self, i: int) -> int:
        t: str = self.text
        j: int = i + 1
        parts: List[str] = []
        chunk_start: int = j
        while j < len(t):
            c: str = t[j]
            if c == '\\':
                j += 2
                continue
            if c == '`':
                break
            if t.startswith('${', j):
                parts.append(t[chunk_start:j])
                self._blank(chunk_start, j)
                parts.append(_PH)
                j = self._scan(j + 2, len(t), top=False)       # 식 끝 `}` 다음
                chunk_start = j
                continue
            j += 1
        parts.append(t[chunk_start:j])
        self._blank(chunk_start, j)
        end: int = min(j + 1, len(t))
        value: str = ''.join(_decode(p) if p != _PH else p for p in parts)
        self.literals.append((i, end, '`', value))
        return end

    def _scan(self, i: int, n: int, top: bool) -> int:
        t: str = self.text
        depth: int = 0
        prev: str = ''
        word: str = ''
        while i < n:
            c: str = t[i]
            if c in ('"', "'"):
                i = self._string(i)
                prev, word = c, ''
                continue
            if c == '`':
                i = self._template(i)
                prev, word = '`', ''
                continue
            if not top:
                if c == '{':
                    depth += 1
                elif c == '}':
                    if depth == 0:
                        return i + 1
                    depth -= 1
            if c == '/' and (prev == '' or prev in _REGEX_PREV or word in _REGEX_WORDS):
                j: int = i + 1
                in_class: bool = False
                while j < n and t[j] != '\n':
                    s: str = t[j]
                    if s == '\\':
                        j += 2
                        continue
                    if s == '[':
                        in_class = True
                    elif s == ']':
                        in_class = False
                    elif s == '/' and not in_class:
                        j += 1
                        break
                    j += 1
                i = j
                prev, word = '/', ''
                continue
            if c.isspace():
                i += 1
                continue
            if c.isalnum() or c in '_$':
                j = i
                while j < n and (t[j].isalnum() or t[j] in '_$'):
                    j += 1
                word = t[i:j]
                prev = t[j - 1]
                i = j
                continue
            prev, word = c, ''
            i += 1
        return i

    def inside_literal(self, offset: int) -> bool:
        return any(a < offset < b for a, b, _q, _v in self.literals)

    def literal_at(self, offset: int) -> Optional[Tuple[int, int, str, str]]:
        if self._starts is None:
            self._starts = {lit[0]: lit for lit in self.literals}
        return self._starts.get(offset)

    def folded(self) -> List[Tuple[int, str]]:
        """문자열 리터럴끼리의 `+` 이어 붙이기를 접은 값 — (첫 리터럴 offset, 접은 값)."""
        quoted = sorted((lit for lit in self.literals if lit[2] in ('"', "'")), key=lambda x: x[0])
        out: List[Tuple[int, str]] = []
        k: int = 0
        while k < len(quoted):
            start, end, _q, value = quoted[k]
            chain: List[str] = [value]
            m: int = k
            while m + 1 < len(quoted) and re.fullmatch(r'\s*\+\s*', self.text[quoted[m][1]:quoted[m + 1][0]]):
                chain.append(quoted[m + 1][3])
                m += 1
            if m > k:
                out.append((start, ''.join(chain)))
            k = m + 1
        return out


def _scheme_hit(value: str) -> bool:
    m = _SCHEME.match(value)
    if not m:
        return value.startswith('//') and re.match(r'//[A-Za-z0-9]', value) is not None
    rest: str = value[m.end():]
    if rest in ('', '//'):
        return False                                   # 스킴만 · 스킴:// 만
    if rest.startswith('//' + _PH):
        return False                                   # `wss://${location.host}` — 주인 자리가 실행 값
    return True


def _domain_hit(value: str) -> bool:
    for m in _DOMAIN.finditer(value):
        tld: str = m.group(2).lower()
        if tld in _STRONG_TLD:
            return True
        before, after = value[:m.start()], value[m.end():]
        if tld in _WEAK_TLD and (before.endswith('//') or before.endswith('@') or after[:1] in ('/', ':', '?', '#')):
            return True
    return False


def _single_literal_arg(view: JsView, pos: int) -> Tuple[bool, Optional[str]]:
    """pos(여는 괄호 다음 또는 쉼표 다음)에서 단일 문자열 리터럴 인자인가 — (단일 리터럴인가, 값)."""
    t: str = view.text
    j: int = pos
    while j < len(t) and t[j].isspace():
        j += 1
    lit = view.literal_at(j)
    if lit is None or lit[2] == '`':
        return False, None
    k: int = lit[1]
    while k < len(t) and t[k].isspace():
        k += 1
    if k < len(t) and t[k] in ',)':
        return True, lit[3]
    return False, None


def _skip_arg(text: str, pos: int) -> Optional[int]:
    """pos 에서 시작하는 인자 하나를 건너뛰고 최상위 쉼표 다음 offset — 없으면 None."""
    depth: int = 0
    i: int = pos
    while i < len(text):
        c: str = text[i]
        if c in '([{':
            depth += 1
        elif c in ')]}':
            if depth == 0:
                return None
            depth -= 1
        elif c == ',' and depth == 0:
            return i + 1
        i += 1
    return None


_CE_TOKEN = re.compile(r'\bcreateElement(NS)?\b')
_SRCDOC_TOKEN = re.compile(r'\bsrcdoc\b')
_DOC_NAMES: Tuple[str, ...] = ('document', 'contentDocument', 'ownerDocument')
_IDENT = re.compile(r'[A-Za-z_$][\w$]*')
_GROUP_WORDS: Set[str] = {'return', 'typeof', 'void', 'await', 'yield', 'case', 'in', 'of', 'delete', 'throw', 'new',
                          'else', 'do'}
_OTHER_RULES: List[Tuple[str, 're.Pattern[str]']] = [
    ('createContextualFragment', re.compile(r'\bcreateContextualFragment\b')),
    ('dynamic import', re.compile(r'\bimport\s*\(|\bimportScripts\s*\(')),
    ('eval·Function', re.compile(r'\beval\s*\(|\bnew\s+Function\b|\bFunction\s*\(|[(,]\s*(?:eval|Function)\s*[),]')),
]
_HTML_SINK = re.compile(r'\b(?:insertAdjacentHTML|innerHTML|outerHTML)\b')
_TIMER = re.compile(r'\bset(?:Timeout|Interval)\s*\(')


def _member_view(view: JsView) -> Tuple[str, Set[int]]:
    """괄호 접근을 점 접근으로 편 코드 뷰 — `x['name']`·`x["name"]`·`` x[`name`] ``(자리표시 없는 리터럴 · 값이 식별자)를
    `x.name` 으로 바꾸고 남는 자리는 공백으로 채운다(offset 은 그대로). 바꾼 리터럴의 시작 offset 도 돌려준다."""
    code: List[str] = list(view.code_text)
    text: str = view.code_text
    used: Set[int] = set()
    for a, b, _q, value in view.literals:
        if _PH in value or not _IDENT.fullmatch(value):
            continue
        i: int = a - 1
        while i >= 0 and text[i].isspace():
            i -= 1
        j: int = b
        while j < len(text) and text[j].isspace():
            j += 1
        if i < 0 or text[i] != '[' or j >= len(text) or text[j] != ']':
            continue
        k: int = i
        lead: str = '.'
        h: int = i - 1
        while h >= 0 and text[h].isspace():
            h -= 1
        if h >= 1 and text[h - 1:h + 1] == '?.':
            k, lead = h - 1, '?.'
        repl: str = lead + value
        span: int = j + 1 - k
        if len(repl) > span:
            continue
        code[k:j + 1] = list(repl + ' ' * (span - len(repl)))
        used.add(a)
    return ''.join(code), used


def _grouped(code: str, start: int, closes: int) -> bool:
    """start(수신자 식 시작)에서 앞으로 여는 괄호 closes 개가 공백만 사이에 두고 이어지고, 맨 바깥 여는 괄호가 호출 괄호가
    아닌가(앞이 식별자·`)`·`]` 가 아니다 — 단 return·typeof 류 낱말 뒤는 묶음 괄호다)."""
    i: int = start - 1
    for _ in range(closes):
        while i >= 0 and code[i].isspace():
            i -= 1
        if i < 0 or code[i] != '(':
            return False
        i -= 1
    while i >= 0 and code[i].isspace():
        i -= 1
    if i < 0:
        return True
    if code[i] in ')]':
        return False
    if code[i].isalnum() or code[i] in '_$':
        j: int = i
        while j >= 0 and (code[j].isalnum() or code[j] in '_$'):
            j -= 1
        return code[j + 1:i + 1] in _GROUP_WORDS
    return True


def _doc_names(mv: str) -> Set[str]:
    """문서 객체 이름 — document·contentDocument·ownerDocument 와 그 지역 별칭(묶음 괄호 · 별칭의 별칭까지)."""
    names: Set[str] = set(_DOC_NAMES)
    chain: str = r'\(*\s*(?:[\w$]+\s*(?:\?\.|\.)\s*)*(%s)(?:\s*\))*\s*(?=[;,\n)]|$)'
    while True:
        rx = re.compile(r'(?<![\w$.])([A-Za-z_$][\w$]*)\s*=(?!=)\s*' + chain % '|'.join(re.escape(n) for n in sorted(names)))
        found: Set[str] = {m.group(1) for m in rx.finditer(mv)} - names
        if not found:
            return names
        names |= found


def scan_js(text: str) -> List[Tuple[int, str]]:
    """기능 JS 외부 코드·주소 덫(WV8) — [(offset, 사유)]. text 는 주석을 지운 JS."""
    view: JsView = JsView(text)
    mv, keyed = _member_view(view)
    hits: List[Tuple[int, str]] = []
    # ① 외부 주소 리터럴 · ② 도메인 꼴 리터럴 (리터럴 단위 · 이스케이프 해제 · `${…}` 자리표시 · 이어 붙이기 접기)
    values: List[Tuple[int, str]] = [(a, v) for a, _b, _q, v in view.literals] + view.folded()
    for offset, value in values:
        if value in _NS_URIS:
            continue
        if _scheme_hit(value):
            hits.append((offset, '외부 주소 리터럴 %r' % value[:60]))
        elif _domain_hit(value):
            hits.append((offset, '도메인 꼴 리터럴 %r' % value[:60]))
    # ③ createElement·createElementNS — 토큰(괄호 접근을 편 뷰) 뒤가 «( + 단일 문자열 리터럴» 이 아니면 발견 · 값이
    #    script 면 발견. 괄호 접근이 아닌 자리의 같은 이름 리터럴(`document[k]` 의 k 값 등)도 발견
    for m in _CE_TOKEN.finditer(mv):
        j: int = m.end()
        while j < len(mv) and mv[j].isspace():
            j += 1
        name: str = m.group(0)
        if j >= len(mv) or mv[j] != '(':
            hits.append((m.start(), '%s 를 호출 밖에서 쓴다(.call·.bind·참조 — 태그 인자 우회)' % name))
            continue
        arg_pos: Optional[int] = j + 1
        if m.group(1):
            arg_pos = _skip_arg(mv, j + 1)
            if arg_pos is None:
                hits.append((m.start(), 'createElementNS 둘째 인자 없음'))
                continue
        ok, value = _single_literal_arg(view, arg_pos)
        if not ok:
            hits.append((m.start(), '%s 태그 인자가 단일 문자열 리터럴이 아니다' % name))
        elif value is not None and value.strip().lower() == 'script':
            hits.append((m.start(), '%s 로 script 요소를 만든다(외부 코드 끌어오기 · 비실행 JSON 은 서버 json_script)'
                         % name))
    for a, _b, _q, value in view.literals:
        if a not in keyed and _PH not in value and value in ('createElement', 'createElementNS'):
            hits.append((a, '%s 이름을 문자열로 쓴다(괄호 접근 · 태그 인자 우회)' % value))
    # ④ srcdoc 토큰(식별자·문자열 모두) · document·contentDocument·ownerDocument(와 그 별칭 · 묶음 괄호 · 괄호 접근)의
    #    write·writeln
    for m in _SRCDOC_TOKEN.finditer(view.code_text):
        hits.append((m.start(), 'srcdoc 사용(같은 출처로 실행되는 문서 주입)'))
    for a, _b, _q, value in view.literals:
        if 'srcdoc' in value.lower():
            hits.append((a, 'srcdoc 문자열(속성 이름 우회)'))
    for name in sorted(_doc_names(mv)):
        guard: str = r'(?<![\w$])' if name in _DOC_NAMES else r'(?<![\w$.])'      # 별칭은 다른 객체의 속성 이름이 아니다
        rx = re.compile(guard + r'%s((?:\s*\))*)\s*(?:\?\.|\.)\s*write(?:ln)?(?![\w$])' % re.escape(name))
        for m in rx.finditer(mv):
            closes: int = m.group(1).count(')')
            if closes:
                begin: int = m.start()
                while begin > 0 and (mv[begin - 1].isalnum() or mv[begin - 1] in '_$.?' or mv[begin - 1].isspace()):
                    begin -= 1
                if not _grouped(mv, begin, closes):
                    continue
            hits.append((m.start(), '%s.write 계열(문서 주입 실행)' % name))
    for m in _HTML_SINK.finditer(view.code_text):
        tail: str = text[m.end():text.find('\n', m.end()) if text.find('\n', m.end()) >= 0 else len(text)]
        if re.search(r'<script', tail, re.I) or any('<script' in v.lower() for a, _b, _q, v in view.literals
                                                     if m.end() <= a < m.end() + len(tail)):
            hits.append((m.start(), 'HTML 주입에 <script'))
    # ⑤ import() · importScripts ⑥ eval·Function ⑦ 문자열 타이머
    for label, rx in _OTHER_RULES:
        for m in rx.finditer(view.code_text):
            hits.append((m.start(), label))
    for m in _TIMER.finditer(view.code_text):
        j = m.end()
        while j < len(text) and text[j].isspace():
            j += 1
        if view.literal_at(j) is not None:
            hits.append((m.start(), '문자열 타이머(문자열 실행)'))
    return sorted(set(hits))


# ------------------------------------------------------------------ 템플릿 참조


_STATIC_TAG = re.compile(r'''\{%\s*static\s+(?:"([^"]+)"|'([^']+)')''')
_RAW_STATIC = re.compile(r'''/static/(web/)?(vendor/[^\s"'<>)]*)''')


def _template_text(ctx: BackstopContext, f: str) -> Tuple[str, object]:
    ms = ctx.mask_of(f)
    text: str = VERBATIM_RE.sub(lambda m: ''.join('\n' if c == '\n' else ' ' for c in m.group()), ms.no_comments)
    return text, ms


def template_refs(ctx: BackstopContext) -> List[Tuple[str, int, str, str, bool]]:
    """web 템플릿의 벤더 참조 — [(템플릿, 행, 종류 static|raw, 가리키는 web-상대 경로, standard prefix)]."""
    out: List[Tuple[str, int, str, str, bool]] = []
    for f in ctx.files:
        if not f.endswith('.html'):
            continue
        text, ms = _template_text(ctx, f)
        if 'vendor' not in text:
            continue
        for m in _STATIC_TAG.finditer(text):
            arg: str = (m.group(1) or m.group(2)).strip()
            std: bool = arg.startswith('web/')
            target: str = 'static/' + (arg[len('web/'):] if std else arg)
            if target.startswith(VENDOR_DIR + '/') or target == VENDOR_DIR:
                out.append((f, ms.line_of(m.start()), 'static', target, std))
        for m in _RAW_STATIC.finditer(text):
            out.append((f, ms.line_of(m.start()), 'raw', 'static/' + m.group(2), False))
    return out


# ------------------------------------------------------------------ 미등재 단위 · 목록 시대


def _tracked_vendor(root: Path) -> Set[str]:
    out: str = _git_text(root, 'ls-files', '-z', '--', 'web/' + VENDOR_DIR)
    return {p[len('web/'):] for p in out.split('\0') if p.startswith('web/')}


def _junk(rel: str, tracked: Set[str]) -> bool:
    return is_os_junk_name(rel.rsplit('/', 1)[-1]) and rel not in tracked


def unit_files(root: Path, unit: str, tracked: Set[str]) -> List[str]:
    """단위의 내용 항목(web-상대) — 일반 파일과 심볼릭 링크(파일·디렉터리 링크 모두 · 따라가지 않고 링크 자체를 센다)."""
    base: Path = root / 'web' / unit.rstrip('/')
    if not unit.endswith('/'):
        return [unit]
    found: List[str] = []
    for cur, dirs, names in os.walk(base):
        dirs.sort()
        rel_dir: str = os.path.relpath(cur, root / 'web').replace(os.sep, '/')
        for d in dirs:
            if os.path.islink(os.path.join(cur, d)):
                found.append(rel_dir + '/' + d)          # 디렉터리 링크 — os.walk 는 따라가지 않으므로 링크를 내용으로 센다
        for name in sorted(names):
            rel: str = rel_dir + '/' + name
            if not _junk(rel, tracked):
                found.append(rel)
    return sorted(found)


def unregistered_units(root: Path, ids: Set[str], tracked: Set[str]) -> List[str]:
    vendor: Path = root / 'web' / VENDOR_DIR
    if not vendor.is_dir():
        return []
    units: List[str] = []
    for name in sorted(os.listdir(vendor)):
        rel: str = VENDOR_DIR + '/' + name
        if os.path.islink(vendor / name):
            if name not in ids:
                units.append(rel)                      # 링크 단위 — 따라가지 않고 링크 자체가 내용이다
        elif (vendor / name).is_dir():
            if name not in ids and unit_files(root, rel + '/', tracked):
                units.append(rel + '/')
        elif name != '.gitattributes' and not _junk(rel, tracked):
            units.append(rel)
    return units


def _registry_shas(text: str) -> Set[str]:
    try:
        data = json.loads(text)
    except ValueError:
        return set()
    out: Set[str] = set()
    sdks = data.get('sdks') if isinstance(data, dict) else None
    for entry in (sdks or {}).values() if isinstance(sdks, dict) else []:
        if isinstance(entry, dict) and isinstance(entry.get('sha256'), str):
            out.add(entry['sha256'])
    return out


def classify_units(root: Path, units: List[str], tracked: Set[str], current_shas: Set[str],
                   registry_now: bool) -> Dict[str, str]:
    """미등재 단위 → WV12(목록 시대 전 내용만) | WV13(목록 시대에 처음 생긴 내용이 하나라도). 얕은 이력은 판정 불가."""
    if not units:
        return {}
    if _git_text(root, 'rev-parse', '--is-shallow-repository').strip() == 'true':
        raise VendorUndecidable('얕은 이력 — 미등재 벤더 단위의 목록 시대 판정 불가(git fetch --unshallow 뒤 다시)')
    prefix: str = _repo_prefix(root) or ''
    reg_spec: str = 'web/' + SDK_REGISTRY
    starts: List[str] = _git_text(root, 'log', '--full-history', '-m', '--diff-filter=A', '--format=%H', 'HEAD',
                                  '--', reg_spec).split()
    if not starts and not registry_now:
        return {u: 'WV12' for u in units}
    era: Set[str] = set()
    for s in starts:
        era.add(s)
        era.update(_git_text(root, 'rev-list', '--ancestry-path', '%s..HEAD' % s).split())
    head: str = _git_text(root, 'rev-parse', '-q', '--verify', 'HEAD').strip()
    head_era: bool = registry_now or head in era
    births: Dict[str, Set[Tuple[str, str]]] = {}
    current: Optional[str] = None
    raw: str = _git_text(root, 'log', '--full-history', '-m', '--raw', '--no-abbrev', '--no-renames',
                         '--format=%x00%H', 'HEAD', '--', 'web/static/')
    for line in raw.split('\n'):
        if line.startswith('\0'):
            current = line[1:].strip()
            continue
        if line.startswith(':') and current:
            meta, _tab, path = line.partition('\t')
            fields: List[str] = meta.split()
            if len(fields) >= 5 and fields[4][:1] in 'AMT' and set(fields[3]) != {'0'}:
                births.setdefault(fields[3], set()).add((current, path))
    history: Set[str] = set(current_shas)
    for c in _git_text(root, 'log', '--full-history', '-m', '--format=%H', 'HEAD', '--', reg_spec).split():
        history |= _registry_shas(_git_text(root, 'show', '%s:%s%s' % (c, prefix, reg_spec)))
    result: Dict[str, str] = {}
    for unit in units:
        era_content: bool = False
        for rel in unit_files(root, unit, tracked):
            path: Path = root / 'web' / rel
            try:
                # 링크는 git 처럼 대상 경로 문자열이 내용이다(따라가지 않는다)
                data: bytes = os.fsencode(os.readlink(path)) if os.path.islink(path) else path.read_bytes()
            except OSError:
                continue
            blob: str = hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()
            born: Set[Tuple[str, str]] = births.get(blob, set())
            born_era: bool = head_era if not born else all(c in era for c, _p in born)
            sha: str = hashlib.sha256(data).hexdigest()
            if not born_era and sha in history:
                if sha not in current_shas:
                    born_era = True              # 등재됐다가 목록에서 빠진 바이트 — 어디에 있든 강등
                elif not any(c not in era and p == prefix + 'web/' + rel for c, p in born):
                    born_era = True              # 지금도 등재된 바이트의 다른 자리 사본(같은 경로 목록 이전 탄생만 예외)
            if born_era:
                era_content = True
                break
        result[unit] = 'WV13' if era_content else 'WV12'
    return result


# ------------------------------------------------------------------ WV10


def _resolve(root: Path, rev: str) -> Optional[str]:
    r = _git(root, 'rev-parse', '--verify', '-q', rev + '^{commit}')
    return r.stdout.decode().strip() if r.returncode == 0 else None


def _find_build(ctx: BackstopContext, design_build: Optional[str]) -> Optional[Path]:
    if design_build is not None:
        path: Path = Path(design_build).resolve()
        return path if (path / 'build-state.json').is_file() else None
    base: Optional[str] = _resolve(ctx.root, ctx.diff_base or '')
    folder: Path = ctx.root / '.dddjango-web'
    if base is None or not folder.is_dir():
        return None
    matches: List[Path] = []
    for state_path in sorted(folder.glob('*/build-state.json')):
        try:
            state = json.loads(state_path.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            continue
        snap = state.get('git_snapshot') if isinstance(state, dict) else None
        if isinstance(snap, str) and snap and _resolve(ctx.root, snap) == base:
            matches.append(state_path.parent)
    return matches[0] if len(matches) == 1 else None


def _recorded(root: Path, state: dict) -> Tuple[Set[str], Set[str]]:
    """빌드 기록 커밋(slices[].commit·commits ∪ sdk_commits) · sdk_commits."""
    def resolve_all(values: List[object]) -> Set[str]:
        out: Set[str] = set()
        for v in values:
            if isinstance(v, str) and re.fullmatch(r'[0-9a-fA-F]{7,40}', v.strip()):
                sha = _resolve(root, v.strip())
                if sha:
                    out.add(sha)
        return out
    values: List[object] = []
    for item in state.get('slices') or []:
        if isinstance(item, dict):
            values.append(item.get('commit'))
            listed = item.get('commits')
            values.extend(listed if isinstance(listed, list) else [listed])
    sdk_values = state.get('sdk_commits')
    sdk: Set[str] = resolve_all(sdk_values if isinstance(sdk_values, list) else [])
    return resolve_all(values) | sdk, sdk


def _wv10(ctx: BackstopContext, design_build: Optional[str]) -> List[Finding]:
    from .debt import DebtError
    from .subst import _approved_merges, _chain, _is_ancestor
    root: Path = ctx.root
    prefix: Optional[str] = _repo_prefix(root)
    if prefix is None or not ctx.gated:
        return []
    targets: List[str] = ['web/' + SDK_REGISTRY, 'web/' + VENDOR_DIR]
    full_reg: str = prefix + targets[0]
    full_vendor: str = prefix + targets[1] + '/'

    def is_target(repo_path: str) -> bool:
        return repo_path == full_reg or repo_path.startswith(full_vendor)

    build: Optional[Path] = _find_build(ctx, design_build)
    if build is None:
        touched: bool = bool(_git_text(root, 'diff', '--name-only', ctx.diff_base or 'HEAD', '--', *targets).strip())
        if touched or (root / 'web' / SDK_REGISTRY).exists() or (root / 'web' / VENDOR_DIR).exists():
            ctx.notices.append('[info] WV10(SDK 변경 격리) 생략 — 빌드 기록 없음(--design-build 또는 git_snapshot 일치 '
                               '빌드가 없다 · 강등 경로는 WV13 이 늘 막는다)')
        return []
    try:
        state = json.loads((build / 'build-state.json').read_text(encoding='utf-8'))
    except (OSError, ValueError) as error:
        ctx.notices.append('[info] WV10 생략 — build-state.json 을 읽을 수 없다(%s)' % error)
        return []
    snapshot: str = state.get('git_snapshot') if isinstance(state.get('git_snapshot'), str) else ''
    base: Optional[str] = _resolve(root, snapshot or (ctx.diff_base or ''))
    if base is None:
        ctx.notices.append('[info] WV10 생략 — git_snapshot 을 풀 수 없다')
        return []
    try:
        chain = _chain(root, base, 'HEAD')
    except DebtError as error:
        ctx.notices.append('[info] WV10 생략 — %s' % error)
        return []
    recorded, sdk = _recorded(root, state)
    try:
        approved, notes = _approved_merges(root, build, base, chain)
        for n in notes:
            ctx.notices.append('[info] WV10 승인 병합 — %s' % n)
    except DebtError as error:
        approved = {}
        ctx.notices.append('[info] WV10 승인 병합 목록 판정 불가 — %s(목록 없음으로 대조)' % error)
    main_ref: Optional[str] = next((r for r in ('main', 'origin/main') if _resolve(root, r)), None)
    out: List[Finding] = []
    fix: str = ('목록·벤더 변경은 Coordinator 가 sdk_vendor.py 로 그 둘만 담은 `chore(web-sdk):` 격리 커밋으로 하고 '
                'build-state sdk_commits 에 적는다 — 슬라이스 커밋에서는 되돌린다.')
    for commit, parents in chain:
        if len(parents) < 2:
            names: List[str] = [n for n in _git_text(root, 'diff-tree', '--no-commit-id', '-r', '--name-only', '-z',
                                                     '--no-renames', '--root', commit).split('\0') if n]
            hit: List[str] = [n for n in names if is_target(n)]
            other: List[str] = [n for n in names if not is_target(n)]
            if commit in sdk:
                if other:
                    out.append(_f('WV10', SDK_REGISTRY, None, 'sdk_commits 커밋 %s 가 목록·벤더 밖 경로도 바꾼다 — %s'
                                  % (commit[:9], ', '.join(other[:5])), fix))
                subject: str = _git_text(root, 'log', '-1', '--format=%s', commit).strip()
                if not subject.startswith(SDK_TITLE):
                    out.append(_f('WV10', SDK_REGISTRY, None, 'sdk_commits 커밋 %s 제목이 `%s` 로 시작하지 않는다'
                                  % (commit[:9], SDK_TITLE), fix))
            elif commit in recorded:
                if hit:
                    out.append(_f('WV10', SDK_REGISTRY, None, '슬라이스 커밋 %s 가 목록·벤더를 바꾼다 — %s'
                                  % (commit[:9], ', '.join(hit[:5])), fix))
            elif hit:
                ctx.notices.append('[info] WV10 기록 밖 커밋 %s 의 목록·벤더 변경(rebase·ff 유입 · 다른 빌드) — '
                                   '내용은 늘 검사가 본다' % commit[:9])
            continue
        evil: Set[str] = {n for n in _git_text(root, 'show', '--cc', '--name-only', '-z', '--format=',
                                               commit).split('\0') if n and is_target(n)}
        if evil:
            out.append(_f('WV10', SDK_REGISTRY, None, '병합 %s 자신의 목록·벤더 몫(두 부모 어느 쪽과도 다름) — %s'
                          % (commit[:9], ', '.join(sorted(evil)[:5])), '병합 해소를 되돌리고 등재 변경은 격리 커밋으로.'))
        upstream: Set[str] = {n for n in _git_text(root, 'diff', '--name-only', '-z', '--no-renames', parents[0],
                                                   commit).split('\0') if n and is_target(n)} - evil
        if not upstream:
            continue
        if commit in approved:
            ctx.notices.append('[info] WV10 승인 병합 %s 의 상류 목록·벤더 몫 — 내용은 늘 검사가 본다' % commit[:9])
        elif main_ref is None:
            ctx.notices.append('[info] WV10 기준 가지 없음 — 승인 목록만 대조')
            out.append(_f('WV10', SDK_REGISTRY, None, '승인 목록 밖 병합 %s 가 목록·벤더를 들여온다' % commit[:9],
                          '기준 가지(main)를 받은 병합이면 기준 가지 참조를 두거나 approved-merges.txt 에 적는다.'))
        elif _is_ancestor(root, parents[1], main_ref):
            ctx.notices.append('[info] WV10 기준 가지 병합 %s 의 상류 목록·벤더 몫 — 내용은 늘 검사가 본다' % commit[:9])
        else:
            out.append(_f('WV10', SDK_REGISTRY, None, '기준 가지 이력 밖 병합 %s(곁가지 재유입)가 목록·벤더를 들여온다'
                          % commit[:9], '곁가지 병합을 되돌리고 등재 변경은 격리 커밋으로.'))
    tracked: Set[str] = _tracked_vendor(root)
    status: List[str] = [e for e in _git_text(root, 'status', '--porcelain', '-z', '--untracked-files=all', '--',
                                              *targets).split('\0') if len(e) > 3]
    dirty: List[str] = []
    for entry in status:
        path: str = entry[3:]
        rel: str = path[len(prefix):][len('web/'):] if path.startswith(prefix + 'web/') else path
        if entry[:2] == '??' and _junk(rel, tracked):
            continue
        dirty.append(path)
    if dirty:
        out.append(_f('WV10', SDK_REGISTRY, None, '목록·벤더의 미커밋 변경 — %s' % ', '.join(dirty[:5]), fix))
    return out


# ------------------------------------------------------------------ 실행


def _copy_bytes(root: Path, entry: dict) -> Optional[bytes]:
    """O7 판정용 등재 사본 바이트 — 꼴이 맞는 일반 파일만(없거나 링크면 None · 바이트 결함은 WV2 가 낸다)."""
    rel = entry.get('file')
    if not isinstance(rel, str) or not rel.startswith(VENDOR_DIR + '/') or '..' in rel.split('/'):
        return None
    path: Path = root / 'web' / rel
    try:
        return path.read_bytes() if path.is_file() and not path.is_symlink() else None
    except OSError:
        return None


def _feature_js(f: str) -> bool:
    return f.startswith('static/js/') and f.lower().endswith('.js')


def run_vendor(ctx: BackstopContext, debt: bool = False, design_build: Optional[str] = None,
               always_only: bool = False) -> List[Finding]:
    """WV 13종 — debt 면 빚 스캔 의미론(WV11·WV12 포함 · WV10 생략), always_only 면 늘 검사(WV1~WV6·WV13)만
    (`sdk_vendor.py verify` · 병합하는 쪽의 확인)."""
    out: List[Finding] = []
    sdk: SdkState = sdk_state(ctx)
    root: Path = ctx.root
    entries: Dict[str, dict] = sdk.entries
    # ---- WV1 · WV3 · WV4 (목록이 있으면 늘)
    if sdk.exists:
        if sdk.error is not None:
            out.append(_f('WV1', SDK_REGISTRY, None, '등재 목록을 엄격 규칙으로 읽을 수 없다 — %s' % sdk.error,
                          '손 편집을 되돌리고 sdk_vendor.py 로만 쓴다(ⓡ2 재정규화는 내용이 같을 때만).'))
        else:
            try:
                if canonical_bytes(sdk.data) != sdk.raw:
                    out.append(_f('WV1', SDK_REGISTRY, None, '정규 바이트가 아니다(키 정렬·2칸·NFC·끝 줄바꿈) — 손 편집·'
                                  '병합 잔재·NFD', '`sdk_vendor.py restore` 의 재정규화(ⓡ2) 또는 도구로 다시 쓴다.'))
            except RegistryError as error:
                out.append(_f('WV1', SDK_REGISTRY, None, str(error), '도구로 다시 쓴다.'))
            for sid, problem in validate_registry(sdk.data):
                out.append(_f('WV1', SDK_REGISTRY, None, ('%s: ' % sid if sid else '') + problem,
                              '항목은 sdk_vendor.py install 로만 쓴다(사람 칸은 entry-draft 에서 · 해시·증거는 도구).'))
            for sid, entry in sorted(entries.items()):
                problems, notes = approval_problems(root, sid, entry)
                for p in problems:
                    out.append(_f('WV3', SDK_REGISTRY, None, '%s: %s' % (sid, p),
                                  'G1 재승인(새 출처)으로 다시 묶거나 승인 기록과 맞는 판으로 되돌린다.'))
                for n in notes:
                    ctx.notices.append('[info] WV3 %s: %s' % (sid, n))
                for key in ('source_url', 'final_url'):
                    reason = lib_cdn_reason(entry.get(key)) if isinstance(entry.get(key), str) else None
                    if reason:
                        out.append(_f('WV4', SDK_REGISTRY, None, '%s: %s 가 %s — 공식 SDK 원본이 아니다' % (sid, key, reason),
                                      '운영자 공식 도메인의 원본만 받는다(라이브러리 CDN 거절).'))
                for d in entry.get('operator_domains') or []:
                    if isinstance(d, str) and d in HOSTING_SUFFIXES:
                        out.append(_f('WV4', SDK_REGISTRY, None, '%s: operator_domains 가 공용 호스팅 접미사 %s 단독'
                                      % (sid, d), '운영자 소유 도메인을 적는다.'))
                file_name: str = entry['file'].rsplit('/', 1)[-1] if isinstance(entry.get('file'), str) else ''
                traps = trap_hits(sid, str(entry.get('name', '')), file_name,
                                  entry.get('source_url', '') if isinstance(entry.get('source_url'), str) else '')
                if traps:
                    out.append(_f('WV4', SDK_REGISTRY, None, '%s: 제외 범주 낱말 %s — 일반 라이브러리는 SDK 가 아니다'
                                  % (sid, ', '.join(traps)), '서버가 만드는 설계나 범위 조정으로 간다(§9 제외).'))
                origins = entry.get('origins')
                if isinstance(origins, dict) and isinstance(origins.get('operator_in_code'), list):
                    if not service_hosts(entry, _copy_bytes(root, entry)):
                        out.append(_f('WV4', SDK_REGISTRY, None, '%s: 주석 밖 코드가 운영자 서비스 호스트를 부르지 않는다'
                                      '(O7 — 배포·문서 자원 경로만 부른다 · 자기 서비스 API 클라이언트가 아니다)' % sid,
                                      '운영자 자기 서비스를 부르지 않으면 제외다.'))
    # ---- WV2 · WV5 (등재 id 디렉터리 — 늘)
    files: Dict[str, str] = sdk.files()
    wv2 = sdk.wv2() if entries else {}
    tracked: Set[str] = _tracked_vendor(root)
    for sid in sorted(entries):
        if wv2.get(sid):
            out.append(_f('WV2', files.get(sid, '%s/%s/' % (VENDOR_DIR, sid)), None,
                          '%s: %s' % (sid, ' · '.join(wv2[sid])),
                          '`sdk_vendor.py restore` 로 등재 바이트를 되쓴다(ⓡ1·ⓡ3) — 원본이 그 바이트를 더 내지 않으면 '
                          '판 올림(G1)·제거·정지.'))
    for sid in sorted(files):
        id_dir: Path = root / 'web' / VENDOR_DIR / sid
        rel_dir: str = '%s/%s/' % (VENDOR_DIR, sid)
        if os.path.islink(id_dir):
            out.append(_f('WV5', rel_dir, None, '%s: 등재 id 디렉터리가 심볼릭 링크' % sid,
                          '일반 디렉터리에 등재 파일 하나만 둔다(`sdk_vendor.py restore`).'))
            continue
        if not id_dir.is_dir():
            continue
        want: str = files[sid]
        for cur, dirs, names in os.walk(id_dir):
            rel_cur: str = os.path.relpath(cur, root / 'web').replace(os.sep, '/')
            for d in sorted(dirs):
                full: Path = Path(cur) / d
                if os.path.islink(full) or not any(True for _ in os.scandir(full)):
                    out.append(_f('WV5', rel_cur + '/' + d + '/', None, '%s: 등재 id 디렉터리 안 하위 디렉터리' % sid,
                                  '등재 파일 하나만 남긴다(미참조면 ⓡ4 제거).'))
            for name in sorted(names):
                rel: str = rel_cur + '/' + name
                if rel == want or _junk(rel, tracked):
                    continue
                out.append(_f('WV5', rel, None, '%s: 등재 id 디렉터리 안 등재 밖 파일' % sid,
                              '아무 템플릿도 부르지 않으면 ⓡ4 로 지운다 — 참조 중이면 등재 파일로 되돌린다(슬라이스 0).'))
    attrs_path: Path = root / 'web' / VENDOR_ATTRS
    if os.path.lexists(attrs_path) and (files or entries):
        if os.path.islink(attrs_path) or not attrs_path.is_file() or attrs_path.read_bytes() != VENDOR_ATTRS_BYTES:
            out.append(_f('WV5', VENDOR_ATTRS, None, 'vendor 표지(.gitattributes)가 고정 바이트가 아니다',
                          '`sdk_vendor.py restore` 로 표지를 다시 쓴다(ⓡ3).'))
    # ---- WV6 (등재 참조 — 늘) · WV11 (빚 스캔)
    refs = template_refs(ctx) if (files or debt) else []
    by_id: Dict[str, str] = files
    for template, line, kind, target, std in refs:
        parts: List[str] = target.split('/')
        sid = parts[2] if len(parts) >= 3 else ''
        if sid not in by_id:
            continue
        reason: Optional[str] = None
        if kind == 'raw':
            reason = '하드코딩 정적 경로 — `{% static \'web/vendor/…\' %}` 로 참조한다'
        elif not std:
            reason = 'standard prefix(`web/`) 밖 참조 `%s`' % target
        elif target != by_id[sid]:
            reason = '등재 파일 밖을 가리킨다 — %s(등재 %s)' % (target, by_id[sid])
        if reason:
            out.append(_f('WV6', template, line, '%s: %s' % (sid, reason),
                          '등재 파일을 `{% static \'web/vendor/<id>/<파일>\' %}` 로 가리킨다(코더 슬라이스 0).'))
    if debt:
        loaded: Set[str] = {target for _t, _l, kind, target, std in refs if kind == 'static' and std}
        for sid, f in sorted(files.items()):
            if f not in loaded:
                out.append(_f('WV11', f, None, '%s: 어느 템플릿도 로드하지 않는 등재 SDK' % sid,
                              '쓰지 않으면 `sdk_vendor.py remove`(사용자 ⓐ/ⓑ 결정).'))
    # ---- WV12 · WV13 (미등재 단위)
    units: List[str] = unregistered_units(root, set(entries), tracked)
    current_shas: Set[str] = {e['sha256'] for e in entries.values() if isinstance(e.get('sha256'), str)}
    kinds: Dict[str, str] = classify_units(root, units, tracked, current_shas, sdk.exists)
    for unit in units:
        if kinds[unit] == 'WV13':
            out.append(_f('WV13', unit, None, '목록 시대에 생긴 미등재 벤더 내용 — 등재 밖으로 나간 길은 `remove` 뿐이다',
                          '참조가 없으면 `sdk_vendor.py remove <루트> <단위 이름>`(미등재 단위째 · 목록 그대로) · 재등록(G1) · '
                          '되돌림만.'))
        elif debt:
            out.append(_f('WV12', unit, None, '미등재 벤더 단위(목록 시대 전) — 이관 항목',
                          '입구: %s.' % _REG_ENTRY))
    if always_only:
        return out
    if debt:
        pre: List[str] = [u for u in units if kinds[u] == 'WV12']
        if pre:
            ctx.notices.append('[info] 미등재 벤더 단위: %s(WV12) — 입구: %s · main 을 받는 레인의 diff 게이트 red 는 '
                               '등록 착륙까지 남는다 · 이 사본이 든 가지는 merge 로 착륙(rebase·squash 면 늘 red)'
                               % (' · '.join(pre), _REG_ENTRY))
    # ---- WV7 · WV8 · WV9 (기능 JS·템플릿 added 줄)
    for f in ctx.files:
        if not ctx.is_touched(f):
            continue
        if _feature_js(f):
            ms = ctx.mask_of(f)
            for offset, reason in scan_js(ms.no_comments):
                line: int = ms.line_of(offset)
                if ctx.line_is_added(f, line):
                    out.append(_f('WV8', f, line, '기능 JS 외부 코드·주소 — %s' % reason,
                                  '외부 스크립트를 끌어오지 않고 외부 주소는 서버가 state 로 넘긴다 · 네트워크는 프로젝트 '
                                  '출처로만(implementation-javascript §8).'))
            if entries:
                for line, reason in _wv7_js(ms.no_comments, entries, ms):
                    if ctx.line_is_added(f, line):
                        out.append(_f('WV7', f, line, reason, '공개 키는 settings → VM → state → data 속성/json_script 로만.'))
                for line, reason in _wv9(ms.no_comments, entries, ms):
                    if ctx.line_is_added(f, line):
                        out.append(_f('WV9', f, line, reason,
                                      '범위 넓힘(G1 한 줄)으로 승인받거나 호출형 API 로 다시 설계한다.'))
        elif f.endswith('.html') and entries:
            text, ms = _template_text(ctx, f)
            for line, reason in _wv7_template(text, entries, ms):
                if ctx.line_is_added(f, line):
                    out.append(_f('WV7', f, line, reason, 'data 속성 값은 `{{ state.<키> }}` 하나만 쓴다.'))
    # ---- WV10 (gated · 빌드 기록)
    if debt:
        if sdk.exists or (root / 'web' / VENDOR_DIR).exists():
            ctx.notices.append('[info] WV10(SDK 변경 격리) 빚 모드 생략 — 빌드 기록 범위 판정은 G2 diff 게이트 몫')
    else:
        out.extend(_wv10(ctx, design_build))
    return out


def _wv7_js(text: str, entries: Dict[str, dict], ms: object) -> List[Tuple[int, str]]:
    view: JsView = JsView(text)
    out: List[Tuple[int, str]] = []
    for sid, entry in entries.items():
        life = entry.get('lifecycle') if isinstance(entry.get('lifecycle'), dict) else {}
        g, init = life.get('global'), life.get('init')
        if not isinstance(g, str) or not isinstance(init, str):
            continue
        rx = re.compile(r'\b%s\s*(?:\??\.\s*%s\b|(?:\?\.)?\s*\[\s*["\']%s["\']\s*\])\s*(?:\?\.)?\s*\(\s*(["\'`])'
                        % (re.escape(g), re.escape(init), re.escape(init)))
        for m in rx.finditer(text):
            if view.inside_literal(m.start()):
                continue
            out.append((ms.line_of(m.start()), '%s: 공개 키 리터럴을 %s.%s 에 직접 넘긴다' % (sid, g, init)))
    return out


_ATTR_VALUE = r'''\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>`]+))'''


def _wv7_template(text: str, entries: Dict[str, dict], ms: object) -> List[Tuple[int, str]]:
    out: List[Tuple[int, str]] = []
    for sid, entry in entries.items():
        for c in entry.get('public_config') or []:
            attr = c.get('attr') if isinstance(c, dict) else None
            if not isinstance(attr, str):
                continue
            for m in re.finditer(r'(?<![\w-])%s%s' % (re.escape(attr), _ATTR_VALUE), text):
                value: str = next(g for g in m.groups() if g is not None)
                if re.fullmatch(r'\s*\{\{[^{}]*\}\}\s*', value) is None:
                    out.append((ms.line_of(m.start()), '%s: %s 값이 순수 `{{ … }}` 가 아니다(키 리터럴)' % (sid, attr)))
    return out


def _call_chains(text: str, view: JsView, global_name: str) -> List[Tuple[int, List[str], int]]:
    """`<global>.<a>.<b>(` 꼴 호출(`?.`·`["b"]` 포함) — [(offset, 이름 사슬, 여는 괄호 offset)]."""
    rx = re.compile(r'\b%s((?:\s*(?:\?\.|\.)\s*[A-Za-z_$][\w$]*|\s*(?:\?\.)?\s*\[\s*(["\'])[A-Za-z_$][\w$]*\2\s*\])+)'
                    r'\s*(?:\?\.)?\s*\(' % re.escape(global_name))
    out: List[Tuple[int, List[str], int]] = []
    for m in rx.finditer(text):
        if view.inside_literal(m.start()):
            continue
        names: List[str] = re.findall(r'[A-Za-z_$][\w$]*', m.group(1))
        out.append((m.start(), names, m.end() - 1))
    return out


def _gateway_url(text: str, view: JsView, paren: int) -> Optional[str]:
    """gateway 호출 첫 인자 객체의 `url:` 문자열 리터럴 값 — 없거나 비리터럴이면 None."""
    code: str = view.code_text
    end: Optional[int] = _skip_arg(code, paren + 1)
    close: int = end if end is not None else len(code)
    depth: int = 0
    i: int = paren + 1
    while i < len(code):
        c = code[i]
        if c in '([{':
            depth += 1
        elif c in ')]}':
            if depth == 0:
                close = min(close, i)
                break
            depth -= 1
        i += 1
    arg: str = code[paren + 1:close]
    m = re.search(r'\burl\s*:\s*', arg)
    if m is None:
        return None
    j: int = paren + 1 + m.end()
    lit = view.literal_at(j)
    if lit is None or _PH in lit[3]:
        return None
    k: int = lit[1]
    while k < len(text) and text[k].isspace():
        k += 1
    if k < len(text) and text[k] not in ',}':
        return None
    return lit[3]


def _wv9(text: str, entries: Dict[str, dict], ms: object) -> List[Tuple[int, str]]:
    view: JsView = JsView(text)
    out: List[Tuple[int, str]] = []
    for sid, entry in entries.items():
        life = entry.get('lifecycle') if isinstance(entry.get('lifecycle'), dict) else {}
        g = life.get('global')
        if not isinstance(g, str):
            continue
        scope: Set[str] = {s for s in entry.get('use_scope') or [] if isinstance(s, str)}
        members: Dict[str, dict] = entry.get('namespace_members') if isinstance(entry.get('namespace_members'), dict) else {}
        gateway_paths: Dict[str, dict] = entry.get('gateway_paths') if isinstance(entry.get('gateway_paths'), dict) else {}
        domains: List[str] = [d for d in entry.get('operator_domains') or [] if isinstance(d, str)]
        for offset, names, paren in _call_chains(text, view, g):
            line: int = ms.line_of(offset)
            if len(names) == 1:
                if '%s.%s' % (g, names[0]) not in scope:
                    out.append((line, '%s: 핵심 함수 %s.%s 가 use_scope 밖' % (sid, g, names[0])))
                continue
            ns, fn = names[0], names[-1]
            table = members.get(ns)
            if not isinstance(table, dict) or not any(
                    (parse_scope_item(s, g) or ('', '', '', ''))[1] == ns for s in scope):
                out.append((line, '%s: 이름공간 %s 는 승인 범위 밖 — 범위 넓힘(G1)' % (sid, ns)))
                continue
            cls = table.get(fn)
            if cls is None:
                out.append((line, '%s: 표에 없는 함수 %s.%s — 표를 고치려면 재승인' % (sid, ns, fn)))
            elif cls == 'sdk_ui':
                out.append((line, '%s: SDK 가 그리는 UI 함수 %s.%s — 어떤 승인으로도 쓰지 않는다' % (sid, ns, fn)))
            elif cls in ('call', 'lifecycle'):
                if '%s.%s.*' % (g, ns) not in scope:
                    out.append((line, '%s: %s.%s — 묶음 %s.%s.* 가 use_scope 밖' % (sid, ns, fn, g, ns)))
            elif cls == 'data_out':
                if '%s.%s.%s' % (g, ns, fn) not in scope:
                    out.append((line, '%s: 사용자 자료를 운영자에 보내는 함수 %s.%s — 이름 지정 원소가 use_scope 에 없다'
                                % (sid, ns, fn)))
            elif cls == 'gateway':
                url = _gateway_url(text, view, paren)
                if url is None:
                    out.append((line, '%s: gateway %s.%s 의 url 이 문자열 리터럴이 아니다' % (sid, ns, fn)))
                    continue
                path, problem = normalize_gateway_url(url, domains)
                if problem:
                    out.append((line, '%s: gateway %s.%s — %s' % (sid, ns, fn, problem)))
                    continue
                known = {p.lower().rstrip('/') or '/': p for p in (gateway_paths.get('%s.%s' % (ns, fn)) or {})}
                if path not in known:
                    out.append((line, '%s: gateway %s.%s 경로 %s 가 api-paths 밖' % (sid, ns, fn, url)))
                elif '%s.%s.%s:%s' % (g, ns, fn, known[path]) not in scope:
                    out.append((line, '%s: gateway %s.%s 경로 %s 는 승인 경로 밖 — 경로마다 범위 넓힘(G1)'
                                % (sid, ns, fn, known[path])))
    return out
