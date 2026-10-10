# PU — 출력 안전 6종 (PU1·PU2·PU3·PU6·PU7·PU8 · PU4·PU5 비움).
# 게이트: PU1=added 파일, 나머지=touched 파일의 added 줄.
#
# *왜 결정적 백스톱인가*: 파일 경로·실행 태그·인라인 JS 채널·자동 이스케이프 우회·동적 실행처럼
# 형태로 환원되는 경계만 검사한다. 기능 JS의 업무 의미·실제 동작은 감수와 브라우저 테스트가 맡는다.
# 외부 JS 는 G1 승인·등재된 공식 SDK 사본(web/static/vendor/<sdk_id>/<파일> — discipline-houserules §9)으로만 들이고
# CDN 실행 태그는 금지한다. 등재 사본의 로드 태그 규칙(속성 · 페이지 block · 그 SDK 를 부르는 기능 JS 앞 ·
# root_view block 여는 줄 앞 · root_view·페이지 중복)은 PU2 벤더 분기가 본다.
# 옛 배치 view/ 페이지는 기능 JS·htmx core 실행 태그의 자리로 받는다 — 벤더 분기는 표준 자리만.
# (바탕: dddjango-web v1.3.1 check_purity.py WP1~WP6 — 번호 그대로 PU 로 · WP4 색 리터럴은 NM10 으로
#  옮겨 PU4 비움 · WP5 motion.js 판형은 러너를 들이지 않아 PU5 비움 · PU7·PU8 = 새 검사 · 벤더 분기 = v1.3.1
#  WP1·WP2 벤더 분기 · base.html 자리 = root/scaffold/view/root_view.html)

from __future__ import annotations

import html
import re
from html.parser import HTMLParser
from typing import Dict, List, Optional, Tuple

from .common import (
    HTMX_CORE, JS_EXTS, ROOT_VIEW_TEMPLATE, VERBATIM_RE, BackstopContext, Finding, base_name_of, ext_of, has_seg,
    is_standard_path, parent_dir_of,
)
from .sdk_registry import VENDOR_DIR, sdk_state

_RULE: str = '제1 규약 §6 출력 안전'
_RULE_SDK: str = 'discipline-houserules §9 공식 SDK'
_HTMX_LEGACY = ('static/js/htmx.min.js', 'static/js/htmx.js')
_FEATURE_JS_RE = re.compile(r'^static/js/[a-z0-9_]+\.js$')

# 인라인 이벤트 핸들러 속성 — 표준 on* 명시 목록 + htmx의 인라인 JS 채널(hx-on)
_ON_ATTR_RE = re.compile(
    r'''(?:^|[\s"'<])(on(?:click|dblclick|change|input|submit|reset|load|unload|error|abort
        |focus|blur|focusin|focusout|keydown|keyup|keypress
        |mousedown|mouseup|mouseover|mouseout|mousemove|mouseenter|mouseleave
        |touchstart|touchend|touchmove|touchcancel
        |drag|dragstart|dragend|dragover|dragenter|dragleave|drop
        |scroll|wheel|contextmenu|select|invalid|toggle|search
        |animationstart|animationend|animationiteration|transitionend
        |pointerdown|pointerup|pointermove|pointerenter|pointerleave|pointercancel
        |pointerover|pointerout|copy|cut|paste|play|pause|ended|canplay|volumechange
        |resize|hashchange|popstate|storage|message)
        |hx-on(?::[\w.:-]+)?)\s*=''',
    re.IGNORECASE | re.VERBOSE)
# htmx의 나머지 인라인 JS 채널 — hx-vals/hx-headers의 js: 접두, hx-trigger의 [조건식]
_HX_JS_VALS_RE = re.compile(r'''hx-(?:vals|headers)\s*=\s*(?:"\s*js:|'\s*js:)''', re.IGNORECASE)
_HX_TRIGGER_COND_RE = re.compile(r'''hx-trigger\s*=\s*(?:"[^"]*\[[^"]*\]|'[^']*\[[^']*\])''', re.IGNORECASE)
# URL 속성의 스크립트 스킴 · srcdoc · 태그로 조립한 스킴 · SVG set/animate 의 href
_URL_ATTRS = frozenset({'href', 'src', 'action', 'formaction', 'xlink:href', 'data', 'poster',
                        'background', 'srcset', 'ping', 'cite'})
_ATTR_RE = re.compile(r'''\s([A-Za-z_:][\w:.-]*)\s*=\s*("([^"]*)"|'([^']*)'|([^\s"'=<>`]+))''')
_TAG_RE = re.compile(r'\{\{.*?\}\}|\{%.*?%\}', re.S)
_CTRL_RE = re.compile(r'[\x00-\x20\x7f]')
_PH: str = ''
_SCHEME_POS_RE = re.compile(r'^[A-Za-z0-9+.\-]*$')
_SVG_HREF_RE = re.compile(r'<(?:set|animate\w*)\b[^>]*attributeName\s*=\s*["\'](?:xlink:)?href["\']', re.I)
_SCRIPT_START_RE = re.compile(r'<script\b', re.IGNORECASE)
_STATIC_ARG_RE = re.compile(r'''\{%\s*static\s+(?:"([^"]+)"|'([^']+)')\s*%\}''')
# 등재 공식 SDK 로드 태그(discipline-houserules §9 «로드») — 속성은 src·defer(·CSP nonce)만
_VENDOR_ATTRS = frozenset({'src', 'defer', 'nonce'})
_BLOCK_SCRIPTS_RE = re.compile(r'\{%-?\s*block\s+scripts\s*-?%\}')
_ENDBLOCK_RE = re.compile(r'\{%-?\s*endblock(?:\s+scripts)?\s*-?%\}')
_REMOTE_RE = re.compile(r'^\s*(?:https?:)?//', re.I)
# PU7 — 자동 이스케이프 우회
_SAFE_TPL_RE = re.compile(r'\|\s*safe(?:seq)?\b|\{%-?\s*autoescape\s+off\b')
_SAFE_PY_RE = re.compile(r'\b(?:mark_safe|SafeString|SafeText)\s*\(')
# PU8 — JS 동적 실행·외부 로드
_JS_DYNAMIC_RE = re.compile(
    r'''\beval\s*\(|\bnew\s+Function\s*\(|\bdocument\.write(?:ln)?\s*\(|\bset(?:Timeout|Interval)\s*\(\s*["'`]'''
    r'''|\bimport\s*\(\s*["'`](?:https?:)?//|\bfrom\s+["'](?:https?:)?//|\bimport\s+["'](?:https?:)?//'''
    r'''|\bcreateElement\s*\(\s*["'`]script["'`]''')


def pu3_url_value(name: str, value: str) -> List[str]:
    """PU3 확장 판정 — URL 속성 값의 스크립트 스킴(엔티티·공백·제어문자 정리 뒤) · srcdoc · 태그로 조립한 스킴."""
    hits: List[str] = []
    if name == 'srcdoc':
        hits.append('srcdoc 속성 — 같은 출처로 실행되는 문서 주입')
    if name in _URL_ATTRS:
        plain: str = _CTRL_RE.sub('', html.unescape(value)).lower()
        if plain.startswith(('javascript:', 'vbscript:', 'data:text/html')):
            hits.append('URL 속성 `%s` 가 스크립트 스킴으로 시작한다' % name)
        assembled: str = _CTRL_RE.sub('', _TAG_RE.sub(_PH, html.unescape(value)))
        i: int = assembled.find(':')
        if i >= 0 and _PH in assembled[:i] and _SCHEME_POS_RE.match(assembled[:i]):
            hits.append('URL 속성 `%s` 의 스킴 자리를 템플릿 태그로 조립한다' % name)
    return hits


def _script_openers(text: str) -> List[Tuple[int, int, str]]:
    """quoted `>`를 건너뛰고 script 시작 태그의 정확한 offset 범위를 돌려준다."""
    out: List[Tuple[int, int, str]] = []
    pos: int = 0
    while True:
        match = _SCRIPT_START_RE.search(text, pos)
        if match is None:
            return out
        i: int = match.end()
        quote: Optional[str] = None
        while i < len(text):
            char = text[i]
            if quote is not None:
                if char == quote:
                    quote = None
            elif char in ('"', "'"):
                quote = char
            elif char == '>':
                i += 1
                break
            i += 1
        out.append((match.start(), i, text[match.start():i]))
        pos = max(i, match.end())


class _StartTagParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.attrs: List[Tuple[str, Optional[str]]] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if tag.lower() == 'script' and not self.attrs:
            self.attrs = attrs


def _attrs_of(tag: str) -> List[Tuple[str, Optional[str]]]:
    parser = _StartTagParser()
    parser.feed(tag)
    return parser.attrs


def _attr_value(attrs: List[Tuple[str, Optional[str]]], name: str) -> Optional[str]:
    values = [value for attr_name, value in attrs if attr_name.lower() == name]
    return values[0] if len(values) == 1 else None


def _has_attr(attrs: List[Tuple[str, Optional[str]]], name: str) -> bool:
    return any(attr_name.lower() == name for attr_name, _ in attrs)


def _local_static_path(attrs: List[Tuple[str, Optional[str]]]) -> Tuple[Optional[str], bool]:
    """정확한 `{% static 'web/…' %}` src를 web-상대 파일로 해소한다. 반환 bool은 표준 `web/` 접두 여부."""
    src = _attr_value(attrs, 'src')
    if src is None:
        return None, False
    match = _STATIC_ARG_RE.fullmatch(src.strip())
    if match is None:
        return None, False
    arg = (match.group(1) or match.group(2)).strip()
    if arg.startswith('web/'):
        return 'static/' + arg[len('web/'):], True
    return 'static/' + arg, False


def _script_location_allowed(path: str) -> bool:
    """실행 script 자리 — root scaffold view 템플릿(문서 셸) 또는 BC 페이지 템플릿(presentation view/)."""
    if not path.endswith('.html') or parent_dir_of(path) != 'view':
        return False
    return path.startswith('root/scaffold/view/') or has_seg(path, 'presentation_layer')


def _legacy_page(path: str) -> bool:
    """옛 배치 view/ 폴더의 페이지 템플릿인가."""
    return not is_standard_path(path) and path.endswith('.html') and parent_dir_of(path) == 'view'


def _is_vendor(path: Optional[str]) -> bool:
    return path is not None and path.startswith(VENDOR_DIR + '/')


def _script_path_allowed(ctx: BackstopContext, path: str, standard_prefix: bool) -> bool:
    if path in _HTMX_LEGACY:
        return path in ctx.base_files  # 브라운필드 설치만 소비
    if not standard_prefix:
        return False
    if _is_vendor(path):
        return path in sdk_state(ctx).passed()  # 등재 · 사본 바이트(WV2) 통과 사본만
    return path == HTMX_CORE or _FEATURE_JS_RE.fullmatch(path) is not None


def _changed(ctx: BackstopContext, f: str, ms, start: int, end: int) -> bool:
    return any(ctx.line_is_added(f, n) for n in range(ms.line_of(start), ms.line_of(max(start, end - 1)) + 1))


def _script_records(ctx: BackstopContext, f: str):
    """템플릿의 script 시작 태그 — (마스킹 본문, [(start, end, attrs, path, standard_prefix)])."""
    ms = ctx.mask_of(f)
    records = []
    for start, end, tag in _script_openers(ms.no_comments):
        attrs = _attrs_of(tag)
        path, std = _local_static_path(attrs)
        records.append((start, end, attrs, path, std))
    return ms, records


def _block_ranges(text: str) -> List[Tuple[int, int]]:
    ranges: List[Tuple[int, int]] = []
    for m in _BLOCK_SCRIPTS_RE.finditer(text):
        end = _ENDBLOCK_RE.search(text, m.end())
        ranges.append((m.start(), end.end() if end else len(text)))
    return ranges


def _sdk_global(ctx: BackstopContext, path: str) -> Optional[str]:
    """등재 SDK 사본(web 상대)의 등재 전역 이름 — `files()` 역대응으로 찾은 그 항목의 `lifecycle.global` 하나.
    이름을 하드코딩하거나 여러 SDK 의 전역을 합치지 않는다. 못 얻으면 None(판독 불명)."""
    state = sdk_state(ctx)
    sid = next((sid for sid, file in state.files().items() if file == path), None)
    lifecycle = state.entries[sid].get('lifecycle') if sid is not None else None
    name = lifecycle.get('global') if isinstance(lifecycle, dict) else None
    return name if isinstance(name, str) and name else None


# 뒤에 오는 `/` 가 정규식 리터럴인 낱말(값이 아니다). 식별자로도 쓸 수 있는 of·yield·await 는 갈림 자리로 둔다.
_JS_REGEX_WORDS = frozenset({'return', 'typeof', 'instanceof', 'in', 'new', 'delete', 'void', 'throw', 'case', 'do', 'else'})
_JS_SPLIT_WORDS = frozenset({'of', 'yield', 'await'})


class _JsCode:
    """PU2 ③ 전용 JS 낱말 가름 — 원문 글자마다 «코드» 인가를 표시한다(주석·문자열·템플릿 글·정규식 리터럴은 코드가
    아니고, 템플릿의 `${…}` 안은 코드다 · 중첩 템플릿과 그 안의 주석을 따라간다). `/` 는 앞 낱말로 가른다 — 값 뒤는
    나눗셈, 연산자·구두점·식 시작 뒤는 정규식이고, `)`·`}`·`++`·`--`·`.`·of·yield·await 뒤는 둘 다 가능해 나눗셈
    (코드)으로 읽는다. 확정하지 못한 자리가 있으면 uncertain 이다: 닫히지 않은 문자열·템플릿·`${`·블록 주석·정규식,
    그리고 갈림 자리의 `/` 가 정규식으로도 읽히면서 그 사이에 따옴표·백틱·역슬래시·`/` 가 있어 뒤 판독이 갈리는 경우.
    WV 검사가 쓰는 mask_js·JsView 와는 따로다(그쪽 동작을 바꾸지 않는다)."""

    def __init__(self, text: str) -> None:
        self.text: str = text
        self.code: List[bool] = [False] * len(text)
        self.uncertain: bool = False
        self._scan(0, True)

    def _scan(self, i: int, top: bool) -> int:
        """코드 구간을 읽는다 — top 이 아니면 `${` 다음에서 시작해 짝 맞는 `}` 다음 offset 을 돌려준다.
        last = 앞 낱말의 갈래: op(뒤 `/` 는 정규식) · value(나눗셈) · split(갈림)."""
        t: str = self.text
        n: int = len(t)
        depth: int = 0
        last: str = 'op'
        while i < n:
            c: str = t[i]
            if c.isspace():
                i += 1
            elif t.startswith('//', i):
                end: int = t.find('\n', i)
                i = n if end < 0 else end
            elif t.startswith('/*', i):
                end = t.find('*/', i + 2)
                if end < 0:
                    self.uncertain = True
                    return n
                i = end + 2
            elif c in '"\'':
                i, last = self._string(i), 'value'
            elif c == '`':
                i, last = self._template(i), 'value'
            elif c == '/':
                i, last = self._slash(i, last)
            elif c.isalnum() or c in '_$' or ord(c) > 127:
                j: int = i
                while j < n and (t[j].isalnum() or t[j] in '_$' or ord(t[j]) > 127):
                    j += 1
                self.code[i:j] = [True] * (j - i)
                word: str = t[i:j]
                last = 'op' if word in _JS_REGEX_WORDS else 'split' if word in _JS_SPLIT_WORDS else 'value'
                i = j
            else:
                if not top and c == '}' and depth == 0:
                    return i + 1
                depth += (c == '{') - (c == '}') if not top else 0
                self.code[i] = True
                if c in '+-' and t.startswith(c * 2, i):  # ++ · -- (후위면 뒤 `/` 는 나눗셈)
                    self.code[i + 1] = True
                    i, last = i + 2, 'split'
                    continue
                last = 'value' if c == ']' else 'split' if c in ')}.' else 'op'
                i += 1
        if not top:
            self.uncertain = True  # `${` 가 닫히지 않았다
        return n

    def _string(self, i: int) -> int:
        t: str = self.text
        j: int = i + 1
        while j < len(t) and t[j] != '\n':
            if t[j] == '\\':
                j += 2
            elif t[j] == t[i]:
                return j + 1
            else:
                j += 1
        self.uncertain = True  # 그 줄에서 닫히지 않은 문자열
        return min(j, len(t))

    def _template(self, i: int) -> int:
        t: str = self.text
        j: int = i + 1
        while j < len(t):
            if t[j] == '\\':
                j += 2
            elif t[j] == '`':
                return j + 1
            elif t.startswith('${', j):
                j = self._scan(j + 2, False)
            else:
                j += 1
        self.uncertain = True  # 닫히지 않은 템플릿
        return len(t)

    def _regex_end(self, i: int) -> Optional[int]:
        """i 의 `/` 를 정규식 리터럴로 읽을 때 닫는 `/` 다음 offset — 그 줄에서 닫히지 않으면 None."""
        t: str = self.text
        j: int = i + 1
        in_class: bool = False
        while j < len(t) and t[j] != '\n':
            if t[j] == '\\':
                j += 2
                continue
            if t[j] == '[':
                in_class = True
            elif t[j] == ']':
                in_class = False
            elif t[j] == '/' and not in_class:
                return j + 1
            j += 1
        return None

    def _slash(self, i: int, last: str) -> Tuple[int, str]:
        t: str = self.text
        end: Optional[int] = self._regex_end(i)
        if last == 'op' and end is not None:  # 정규식 리터럴(플래그 포함) — 코드가 아니다
            while end < len(t) and (t[end].isalnum() or t[end] in '_$'):
                end += 1
            return end, 'value'
        if last == 'op' or (last == 'split' and end is not None and any(ch in t[i + 1:end - 1] for ch in '\'"`\\/')):
            self.uncertain = True  # 정규식 자리인데 닫히지 않았거나, 나눗셈·정규식에 따라 뒤 판독이 갈린다
        self.code[i] = True
        return i + 1, 'op'


def _js_reference_lines(source: str, name: str) -> Optional[Tuple[int, ...]]:
    """JS 원문의 코드 부분에서 name 이 식별자 경계(앞뒤가 영숫자·`_`·`$` 가 아님)로 나오는 행.
    원문 어디에도 그 이름이 없으면 빈 tuple 이고, 가름을 확정하지 못했는데(_JsCode.uncertain) 코드 밖으로 읽힌
    이름이 있으면 None(판독 불명) — 실제 참조를 «참조 없음» 으로 놓치지 않는다."""
    hits: List[int] = [m.start() for m in re.finditer(r'(?<![\w$])' + re.escape(name) + r'(?![\w$])', source)]
    if not hits:
        return ()
    view = _JsCode(source)
    code: List[int] = [offset for offset in hits if view.code[offset]]
    if view.uncertain and len(code) != len(hits):
        return None
    return tuple(sorted({source.count('\n', 0, offset) + 1 for offset in code}))


def _sdk_reference_lines(ctx: BackstopContext, js: str, name: Optional[str]) -> Optional[Tuple[int, ...]]:
    """기능 JS(web 상대) 원문의 코드 부분에서 등재 전역 이름이 식별자 경계로 나오는 행 — «그 SDK 를 부르는 JS» 판정.

    코드 부분 = 주석·문자열·템플릿 글·정규식 리터럴 밖(템플릿 리터럴의 `${…}` 안은 코드 — `_JsCode`). 식별자 경계 =
    이름 앞뒤가 영숫자·`_`·`$` 가 아님(`window.<전역>`·`globalThis.<전역>` 의 점 뒤는 받는다).
    판정 범위: 등재 전역 이름을 담은 보수적 소비 후보 판정이다 — 같은 이름의 지역 변수·다른 객체 속성은 소비로
    센다(과보고). `window["<전역>"]` 같은 문자열 접근과 다른 JS 를 거친 간접 호출은 못 본다(감수 몫).
    판독 불명(원문 없음·디코드 실패·등재 전역 불명·가름을 확정하지 못한 원문에서 코드 밖으로 읽힌 이름)은 None —
    호출 쪽이 «부르는 것» 으로 센다. 읽기는 ctx.web / js, 행은 원문 행(added 조회와 같은 web 상대 좌표)이다."""
    cache: Dict[Tuple[str, Optional[str]], Optional[Tuple[int, ...]]] = getattr(ctx, '_sdk_reference_cache', None)
    if cache is None:
        cache = {}
        setattr(ctx, '_sdk_reference_cache', cache)
    key = (js, name)
    if key not in cache:
        cache[key] = None
        if name is not None:
            try:
                cache[key] = _js_reference_lines((ctx.web / js).read_text(encoding='utf-8'), name)
            except (OSError, UnicodeError, RecursionError):
                pass
    return cache[key]


def _sdk_reference_added(ctx: BackstopContext, js: str, lines: Optional[Tuple[int, ...]]) -> bool:
    """그 기능 JS 의 등재 전역 참조 행이 이번 변경의 added 인가 — 판독 불명이면 그 JS 가 touched 인가."""
    return ctx.is_touched(js) if lines is None else any(ctx.line_is_added(js, line) for line in lines)


def _vendor_order_reasons(ctx: BackstopContext, f: str, ms, records) -> List[Tuple[int, str]]:
    """③ 등재 SDK 태그가 그 SDK 를 부르는 기능 JS 태그보다 뒤 — (태그 offset, 사유).

    소비 JS = SDK 태그보다 앞선 표준 기능 JS 태그 가운데 `_sdk_reference_lines` 가 참조 행을 찾았거나 판독 불명인
    파일. 발화 게이트 = 앞선 소비 JS 가 하나 이상이고 (가) SDK 태그 줄이 added 이거나 (나) 앞선 소비 JS 태그 줄이
    added 이거나 (다) 앞선 소비 JS 의 전역 참조 행이 added(판독 불명인 그 JS 가 touched 인 경우 포함). (다) 는
    템플릿이 그대로여도 낸다 — 그런 템플릿은 `_vendor_order_templates` 가 ③ 에만 올린다."""
    out: List[Tuple[int, str]] = []
    features = [(s, e, path) for s, e, _a, path, std in records
                if path is not None and std and _FEATURE_JS_RE.fullmatch(path)]
    passed = sdk_state(ctx).passed()
    for start, end, _attrs, path, std in records:
        if not (std and path in passed):
            continue
        name = _sdk_global(ctx, path)
        before = []
        for s, e, js in features:
            if s < start:
                lines = _sdk_reference_lines(ctx, js, name)
                if lines is None or lines:
                    before.append((s, e, js, lines))
        if before and (_changed(ctx, f, ms, start, end) or any(
                _changed(ctx, f, ms, s, e) or _sdk_reference_added(ctx, js, lines) for s, e, js, lines in before)):
            out.append((start, '등재 SDK 태그가 그 SDK 를 부르는 기능 JS 태그보다 뒤 — %s(앞선: %s)' %
                        (path, ', '.join(js for _s, _e, js, _lines in before))))
    return out


def _vendor_order_templates(ctx: BackstopContext) -> Dict[str, tuple]:
    """③ 전용 교차 색인 — 이번 변경에서 등재 전역 참조 행이 added 인 기능 JS(또는 touched 인데 판독 불명인 기능 JS)를
    그 SDK 태그보다 앞에 싣는, 손 안 댄 템플릿(페이지 view·root_view) → (마스킹 본문, script 기록).
    그런 JS 가 없으면 템플릿을 읽지 않는다. 다른 PU 검사를 이 템플릿으로 넓히지 않는다."""
    if not ctx.gated:
        return {}
    features = [f for f in ctx.files if _FEATURE_JS_RE.fullmatch(f) and ctx.is_touched(f)]
    if not features:
        return {}
    changed: Dict[str, set] = {}
    for sdk in sdk_state(ctx).passed():
        name = _sdk_global(ctx, sdk)
        consumers = {js for js in features if _sdk_reference_added(ctx, js, _sdk_reference_lines(ctx, js, name))}
        if consumers:
            changed[sdk] = consumers
    if not changed:
        return {}
    templates: Dict[str, tuple] = {}
    for f in ctx.files:
        if ctx.is_touched(f) or not _script_location_allowed(f):
            continue
        ms, records = _script_records(ctx, f)
        if any(std and path in changed and any(js_std and js in changed[path] and s < start
               for s, _e, _a, js, js_std in records) for start, _end, _attrs, path, std in records):
            templates[f] = (ms, records)
    return templates


def _vendor_reasons(ctx: BackstopContext, f: str, ms, records, root_vendor: Dict[str, bool]) -> List[Tuple[int, str]]:
    """등재 SDK 로드 태그 규칙(discipline-houserules §9 «로드») — ① 속성 ② 페이지 block 밖 ③ 그 SDK 를 부르는 기능 JS 뒤
    ④ root_view block 여는 줄 뒤 ⑤ root_view·페이지 중복. ③⑤ 는 벤더 태그나 상대 태그 어느 쪽 줄이 added 여도 낸다
    (③ 의 소비 JS 판정·게이트는 `_vendor_order_reasons`)."""
    out: List[Tuple[int, str]] = []
    passed = sdk_state(ctx).passed()
    text: str = ms.no_comments
    blocks = _block_ranges(text)
    is_root: bool = f == ROOT_VIEW_TEMPLATE
    order_reasons = dict(_vendor_order_reasons(ctx, f, ms, records))
    block_lines: bool = any(_changed(ctx, f, ms, m.start(), m.end())
                            for rx in (_BLOCK_SCRIPTS_RE, _ENDBLOCK_RE) for m in rx.finditer(text))
    for start, end, attrs, path, std in records:
        if not (std and path in passed):
            continue
        changed: bool = _changed(ctx, f, ms, start, end)
        extra = sorted({name.lower() for name, _v in attrs} - _VENDOR_ATTRS - {'async'})  # async 는 공통 사유가 낸다
        if changed and extra:
            out.append((start, '등재 SDK 태그 속성은 src·defer(·CSP nonce)만 — %s · %s' % (', '.join(extra), path)))
        if not is_root and (changed or block_lines) and not any(a <= start < b for a, b in blocks):
            out.append((start, '등재 SDK 태그가 페이지 `{%% block scripts %%}` 밖 — %s' % path))
        if start in order_reasons:
            out.append((start, order_reasons[start]))
        if is_root and (changed or block_lines) and any(a < start for a, _b in blocks):
            out.append((start, '등재 SDK 태그가 root_view 의 `{%% block scripts %%}` 여는 줄보다 뒤 — %s' % path))
        if not is_root and path in root_vendor and (changed or root_vendor[path]):
            out.append((start, 'root_view·페이지 중복 로드 — %s(root_view 가 이미 싣는다)' % path))
    return out


def _root_vendor(ctx: BackstopContext) -> Dict[str, bool]:
    """root_view.html 이 싣는 등재 SDK 경로 → 그 태그 줄이 added 인가."""
    if ROOT_VIEW_TEMPLATE not in ctx.files_set or not any(f.startswith(VENDOR_DIR + '/') for f in ctx.all_files):
        return {}
    ms, records = _script_records(ctx, ROOT_VIEW_TEMPLATE)
    passed = sdk_state(ctx).passed()
    found: Dict[str, bool] = {}
    for start, end, _attrs, path, std in records:
        if std and path in passed:
            found[path] = found.get(path, False) or _changed(ctx, ROOT_VIEW_TEMPLATE, ms, start, end)
    return found


def run_purity(ctx: BackstopContext) -> List[Finding]:
    out: List[Finding] = []
    root_vendor: Dict[str, bool] = _root_vendor(ctx)
    order_templates = _vendor_order_templates(ctx)
    vendor_seen: set = set()
    fix_vendor: str = ("등재 SDK 는 `{% static 'web/vendor/<sdk_id>/<파일>' %}` 외부 태그 하나로, 속성 src·defer 만, 그 SDK 를 "
                       '쓰는 페이지의 `{% block scripts %}` 안 그 SDK 를 부르는 기능 JS 태그보다 앞에 둔다(모든 페이지가 쓰면 root_view 의 '
                       'block 여는 줄 앞 · 중복 금지 — discipline-houserules §9).')

    def vendor_findings(f: str, ms, records, order_only: bool = False) -> None:
        reasons = (_vendor_order_reasons(ctx, f, ms, records) if order_only
                   else _vendor_reasons(ctx, f, ms, records, root_vendor))
        for start, reason in reasons:
            if (f, start, reason) not in vendor_seen:
                vendor_seen.add((f, start, reason))
                out.append(Finding('PU2', f, ms.line_of(start), reason, _RULE_SDK, fix_vendor))

    for f in ctx.files:
        ext: str = ext_of(f)
        vendored: bool = f.startswith('static/vendor/') or f == HTMX_CORE or f in _HTMX_LEGACY

        # ---- PU1: 신규 JS 경로·형태 + core 예약 이름 · 벤더 자리는 등재 공식 SDK 사본만
        if ext in JS_EXTS and ctx.is_added(f) and _is_vendor(f):
            if f not in sdk_state(ctx).files().values():
                out.append(Finding('PU1', f, None,
                    '등재되지 않은 벤더 JS — static/vendor/ 에는 G1 승인·등재된 공식 SDK 사본만 둔다', _RULE_SDK,
                    '공식 SDK 면 G1 승인 뒤 Coordinator 가 sdk_vendor.py 로 등재하고, 아니면 제3자 JS 를 들이지 않는다.'))
        elif ext in JS_EXTS and ctx.is_added(f):
            if f in _HTMX_LEGACY:
                out.append(Finding('PU1', f, None,
                    'htmx legacy core 예약 이름 `%s` 신설 — 기존 설치로만 소비 가능' % base_name_of(f), _RULE,
                    '신규 core는 %s 하나만 설치한다.' % HTMX_CORE))
            elif f != HTMX_CORE and not _FEATURE_JS_RE.fullmatch(f):
                out.append(Finding('PU1', f, None,
                    '신규 JavaScript 경로·형태 위반 — 기능 JS는 static/js/<기능>.js snake_case 평면 한 파일, '
                    '외부 JS는 등재된 공식 SDK 사본(static/vendor/<sdk_id>/<파일>)만', _RULE,
                    '중첩·다른 폴더·`.min.js`·`.mjs`·`.cjs` 없이 static/js/<기능>.js로 둔다.'))

        # ---- PU2 벤더 분기 ⑤ root_view·페이지 중복: root_view 태그 줄만 added 여도 페이지 파일에 낸다(교차 파일 색인)
        if (ext == '.html' and not ctx.is_touched(f) and f != ROOT_VIEW_TEMPLATE
                and any(root_vendor.values()) and _script_location_allowed(f)):
            page_ms, page_records = _script_records(ctx, f)
            vendor_findings(f, page_ms, page_records)

        if f in order_templates:
            page_ms, page_records = order_templates[f]
            vendor_findings(f, page_ms, page_records, order_only=True)

        if not ctx.is_touched(f):
            continue

        if ext == '.html':
            ms = ctx.mask_of(f)
            # ---- PU6: Django는 다중줄 {# #}를 주석으로 해석하지 않는다(내용이 응답에 노출)
            template_text: str = VERBATIM_RE.sub(
                lambda m: ''.join('\n' if c == '\n' else ' ' for c in m.group()), ms.no_comments)
            for m in re.finditer(r'\{#.*?(?:#\}|$)', template_text, re.DOTALL):
                if _changed(ctx, f, ms, m.start(), m.end()):
                    out.append(Finding('PU6', f, ms.line_of(m.start()),
                        'Django 짧은 주석이 닫히지 않았거나 여러 줄이다 — 주석 내용이 응답에 노출된다', _RULE,
                        '한 줄은 {# … #}, 여러 줄은 {% comment %}…{% endcomment %}를 쓴다.'))

            # ---- PU2: 실행 script — 로컬 static 외부 참조 · 허용 경로 · 자리 · 실행 순서 · CDN 금지
            _ms, records = _script_records(ctx, f)
            path_counts: Dict[str, int] = {}
            for _s, _e, _a, path, _std in records:
                if path is not None:
                    path_counts[path] = path_counts.get(path, 0) + 1
            for start, end, attrs, path, std in records:
                if not _changed(ctx, f, ms, start, end):
                    continue
                reason: Optional[str] = None
                src: Optional[str] = _attr_value(attrs, 'src')
                if src is not None and _REMOTE_RE.match(src):
                    reason = 'CDN 실행 태그 금지 — %s' % src.strip()
                elif path is None:
                    reason = '실행 script는 실제 src 속성의 정확한 `{% static %}` 외부 참조여야 한다(인라인 script 금지)'
                elif path not in ctx.files_set:
                    reason = 'script src가 가리키는 로컬 static 파일 없음 — %s' % path
                elif not _script_path_allowed(ctx, path, std):
                    reason = 'script src 경로가 기능 JS·htmx core·등재 공식 SDK 사본(WV2 통과) 경로가 아니다 — %s' % path
                elif not (_script_location_allowed(f) or (_legacy_page(f) and not _is_vendor(path))):
                    reason = '실행 script 위치 위반 — 조각(section·widget·component)이 아니라 root_view 또는 페이지 view 템플릿이어야 한다'
                elif _has_attr(attrs, 'async'):
                    reason = 'async 실행 금지 — DOM·의존 순서를 보존한다 — %s' % path
                elif ((_is_vendor(path) or (_attr_value(attrs, 'type') or '').strip().lower() != 'module')
                      and not _has_attr(attrs, 'defer')):
                    reason = 'classic 외부 스크립트는 defer가 필요하다 — %s' % path
                elif path_counts.get(path, 0) > 1:
                    reason = '같은 템플릿의 script 중복 로드 — %s' % path
                if reason is not None:
                    out.append(Finding('PU2', f, ms.line_of(start), reason, _RULE,
                        "실재하는 로컬 파일을 `{% static 'web/…' %}`로 한 번 참조하고, classic은 defer·module은 "
                        'type="module"을 쓰며 async와 조각 로드를 제거한다 — 외부 JS 는 G1 승인·등재된 공식 SDK 사본'
                        "(`{% static 'web/vendor/<sdk_id>/<파일>' %}`)만."))
            if _script_location_allowed(f) and (root_vendor or any(_is_vendor(r[3]) for r in records)):
                vendor_findings(f, ms, records)

            # ---- PU3: 인라인 이벤트 핸들러·htmx JS 채널·스크립트 스킴 금지
            for m in _ON_ATTR_RE.finditer(ms.no_comments):
                line: int = ms.line_of(m.start(1))
                if ctx.line_is_added(f, line):
                    out.append(Finding('PU3', f, line,
                        '인라인 이벤트 핸들러 `%s=` — 속성 속 JS도 커스텀 JS다' % m.group(1).strip(), _RULE,
                        '서버 요청은 HTMX 선언으로, 승인된 브라우저 UI 상호작용은 외부 기능 JS로 옮긴다.'))
            for rx, msg in ((_HX_JS_VALS_RE, 'htmx `js:` 채널 — hx-vals/hx-headers의 `js:` 접두는 htmx가 eval하는 임의 JS다'),
                            (_HX_TRIGGER_COND_RE, 'hx-trigger `[조건식]` — 대괄호 이벤트 필터는 htmx가 eval하는 임의 JS다'),
                            (_SVG_HREF_RE, 'SVG set/animate 가 href 를 바꾼다 — 링크 주소를 실행 시점에 바꾸는 채널')):
                for m in rx.finditer(ms.no_comments):
                    line = ms.line_of(m.start())
                    if ctx.line_is_added(f, line):
                        out.append(Finding('PU3', f, line, msg, _RULE,
                            '조건·값은 서버 판정 또는 승인된 외부 기능 JS가 소유한다 — 속성에는 정적 값만 쓴다.'))
            for m in _ATTR_RE.finditer(ms.no_comments):
                name: str = m.group(1).lower()
                if name != 'srcdoc' and name not in _URL_ATTRS:
                    continue
                value: str = next(g for g in (m.group(3), m.group(4), m.group(5)) if g is not None)
                line = ms.line_of(m.start(1))
                if not ctx.line_is_added(f, line):
                    continue
                for reason in pu3_url_value(name, value):
                    out.append(Finding('PU3', f, line, reason, _RULE,
                        '스크립트는 외부 기능 JS 로만 실행한다 — 링크·폼 주소는 State 의 href 만 쓰고 스킴을 템플릿 태그로 조립하지 않는다.'))

            # ---- PU7(템플릿): 자동 이스케이프 우회
            for m in _SAFE_TPL_RE.finditer(ms.no_comments):
                line = ms.line_of(m.start())
                if ctx.line_is_added(f, line):
                    out.append(Finding('PU7', f, line, '자동 이스케이프 우회 `%s`' % m.group(0).strip(), _RULE,
                        '값은 자동 이스케이프된 `{{ }}` 로만 출력한다 — 마크업이 필요하면 조각 템플릿으로 조립한다.'))

        if ext == '.py':
            ms = ctx.mask_of(f)
            # ---- PU7(Python): mark_safe·SafeString — 이스케이프되지 않은 문자열 생성
            for m in _SAFE_PY_RE.finditer(ms.tokens_view):
                line = ms.line_of(m.start())
                if ctx.line_is_added(f, line):
                    out.append(Finding('PU7', f, line, '자동 이스케이프 우회 `%s`' % m.group(0).rstrip('( '), _RULE,
                        'Python 에서 마크업을 만들지 않는다 — 값만 State 에 담고 템플릿이 이스케이프 출력한다.'))

        # ---- PU8: 기능 JS 의 동적 실행·외부 로드
        if ext in JS_EXTS and not vendored:
            ms = ctx.mask_of(f)
            for m in _JS_DYNAMIC_RE.finditer(ms.no_comments):
                line = ms.line_of(m.start())
                if ctx.line_is_added(f, line):
                    out.append(Finding('PU8', f, line, 'JS 동적 실행·외부 로드 `%s`' % m.group(0).strip(), _RULE,
                        'eval·Function·document.write·문자열 타이머·원격 import·script 요소 생성 없이 정적 코드만 쓴다 — '
                        '외부 JS 는 G1 승인·등재된 공식 SDK 사본을 페이지에서 defer 로 싣는다.'))
    return out
