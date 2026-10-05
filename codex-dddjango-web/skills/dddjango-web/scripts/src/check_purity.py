# PU — 출력 안전 6종 (PU1·PU2·PU3·PU6·PU7·PU8 · PU4·PU5 비움).
# 게이트: PU1=added 파일, 나머지=touched 파일의 added 줄.
#
# *왜 결정적 백스톱인가*: 파일 경로·실행 태그·인라인 JS 채널·자동 이스케이프 우회·동적 실행처럼
# 형태로 환원되는 경계만 검사한다. 기능 JS의 업무 의미·실제 동작은 감수와 브라우저 테스트가 맡는다.
# 외부 JS 는 web/static/vendor/<라이브러리>/<버전>/ 고정 사본으로만 들이고 CDN 실행 태그는 금지한다.
# (바탕: dddjango-web v1.3.1 check_purity.py WP1~WP6 — 번호 그대로 PU 로 · WP4 색 리터럴은 NM10 으로
#  옮겨 PU4 비움 · WP5 motion.js 판형은 러너를 들이지 않아 PU5 비움 · PU7·PU8 = 새 검사)

from __future__ import annotations

import html
import re
from html.parser import HTMLParser
from typing import Dict, List, Optional, Tuple

from .common import (
    HTMX_CORE, JS_EXTS, VERBATIM_RE, BackstopContext, Finding, base_name_of, ext_of, has_seg,
    parent_dir_of, segs_of,
)

_RULE: str = '제1 규약 §6 출력 안전'
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


def _is_vendor_copy(path: str) -> bool:
    s: List[str] = segs_of(path)
    return len(s) == 5 and s[:2] == ['static', 'vendor']


def _script_path_allowed(ctx: BackstopContext, path: str, standard_prefix: bool) -> bool:
    if path in _HTMX_LEGACY:
        return path in ctx.base_files  # 브라운필드 설치만 소비
    if not standard_prefix:
        return False
    return path == HTMX_CORE or _is_vendor_copy(path) or _FEATURE_JS_RE.fullmatch(path) is not None


def _changed(ctx: BackstopContext, f: str, ms, start: int, end: int) -> bool:
    return any(ctx.line_is_added(f, n) for n in range(ms.line_of(start), ms.line_of(max(start, end - 1)) + 1))


def run_purity(ctx: BackstopContext) -> List[Finding]:
    out: List[Finding] = []
    for f in ctx.files:
        ext: str = ext_of(f)
        vendored: bool = f.startswith('static/vendor/') or f == HTMX_CORE or f in _HTMX_LEGACY

        # ---- PU1: 신규 JS 경로·형태 + core 예약 이름
        if ext in JS_EXTS and ctx.is_added(f) and not f.startswith('static/vendor/'):
            if f in _HTMX_LEGACY:
                out.append(Finding('PU1', f, None,
                    'htmx legacy core 예약 이름 `%s` 신설 — 기존 설치로만 소비 가능' % base_name_of(f), _RULE,
                    '신규 core는 %s 하나만 설치한다.' % HTMX_CORE))
            elif f != HTMX_CORE and not _FEATURE_JS_RE.fullmatch(f):
                out.append(Finding('PU1', f, None,
                    '신규 JavaScript 경로·형태 위반 — 기능 JS는 static/js/<기능>.js snake_case 평면 한 파일, '
                    '외부 JS는 static/vendor/<라이브러리>/<버전>/ 고정 사본만', _RULE,
                    '중첩·다른 폴더·`.min.js`·`.mjs`·`.cjs` 없이 static/js/<기능>.js로 둔다.'))

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
            records = []
            path_counts: Dict[str, int] = {}
            for start, end, tag in _script_openers(ms.no_comments):
                attrs = _attrs_of(tag)
                path, std = _local_static_path(attrs)
                records.append((start, end, attrs, path, std))
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
                    reason = 'script src 경로가 기능 JS·htmx core·vendor 고정 사본 경로가 아니다 — %s' % path
                elif not _script_location_allowed(f):
                    reason = '실행 script 위치 위반 — 조각(section·widget·component)이 아니라 root_view 또는 페이지 view 템플릿이어야 한다'
                elif _has_attr(attrs, 'async'):
                    reason = 'async 실행 금지 — DOM·의존 순서를 보존한다 — %s' % path
                elif (_attr_value(attrs, 'type') or '').strip().lower() != 'module' and not _has_attr(attrs, 'defer'):
                    reason = 'classic 외부 스크립트는 defer가 필요하다 — %s' % path
                elif path_counts.get(path, 0) > 1:
                    reason = '같은 템플릿의 script 중복 로드 — %s' % path
                if reason is not None:
                    out.append(Finding('PU2', f, ms.line_of(start), reason, _RULE,
                        "실재하는 로컬 파일을 `{% static 'web/…' %}`로 한 번 참조하고, classic은 defer·module은 "
                        'type="module"을 쓰며 async와 조각 로드를 제거한다 — 외부 JS 는 static/vendor/<라이브러리>/<버전>/ 고정 사본으로.'))

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
                        '외부 JS 는 static/vendor/<라이브러리>/<버전>/ 고정 사본을 페이지에서 defer 로 싣는다.'))
    return out
