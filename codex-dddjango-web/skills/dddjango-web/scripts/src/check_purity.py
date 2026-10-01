# WP — UI 실행 경계·템플릿 출력 6종 (값 정본: discipline-web-houserules §5⑤·§7).
# 게이트: WP1=added 파일, WP2~WP4=touched 파일의 added 줄, WP5=touched·added된 motion.js 전체.
#
# *왜 결정적 백스톱인가*: 파일 경로·실행 태그·인라인 채널·색 리터럴·motion 판형처럼
# 형태로 환원되는 경계만 검사한다. 기능 JS의 업무 의미·기능 일대일·실제 동작은 감수와
# 브라우저 증거가 맡는다. (판형: dddart check_pubspec의 «토대 불변식» PJ 패밀리)

import hashlib
import html
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import List, Optional, Tuple

from .common import (BackstopContext, Finding, HTMX_ALLOWED, HTMX_CANONICAL,
                     HTMX_LEGACY, MOTION_JS, VENDOR_DIR, VERBATIM_RE, base_name_of,
                     ext_of, parent_dir_of)

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
_HX_JS_VALS_RE = re.compile(
    r'''hx-(?:vals|headers)\s*=\s*(?:"\s*js:|'\s*js:)''', re.IGNORECASE)
_HX_TRIGGER_COND_RE = re.compile(
    r'''hx-trigger\s*=\s*(?:"[^"]*\[[^"]*\]|'[^']*\[[^']*\])''', re.IGNORECASE)

# 색 리터럴 — #hex(3·4·6·8, HTML 엔티티 `&#…;` 제외)·rgb()·hsl() 계열
_COLOR_RE = re.compile(
    r'(?<!&)#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})(?![0-9a-zA-Z_-])'
    r'|\b(?:rgb|rgba|hsl|hsla)\s*\(')

_TOKENS_CSS = 'design_system/foundation/tokens.css'

# <script> opener를 quote-aware로 모은 뒤 HTMLParser로 실제 속성만 읽는다.
_SCRIPT_START_RE = re.compile(r'<script\b', re.IGNORECASE)
_STATIC_ARG_RE = re.compile(
    r'''\{%\s*static\s+(?:"([^"]+)"|'([^']+)')\s*%\}''')
_FEATURE_JS_RE = re.compile(r'^static/js/[a-z0-9_]+\.js$')

# WP1 core 중복 사유 · WP2 실행 순서 사유 — 빚 스캔의 브라운필드 면제(src/debt.py)가 발견
# 문자열만으로 legacy core 설치·로드 태그를 식별한다. WP2 사유 끝에는 ` — <src 경로>` 가 붙는다.
WP1_CORE_DUPLICATE_REASON: str = 'HTMX core 중복 — canonical과 legacy 설치를 합쳐 한 파일이어야 한다'
WP2_ASYNC_REASON: str = 'async 실행 금지 — DOM·의존 순서를 보존한다'
WP2_DEFER_REASON: str = 'classic 외부 스크립트는 defer가 필요하다'

# 등재 공식 SDK 로드 태그(houserules §9 «로드») — 속성은 src·defer(·CSP nonce)만
_VENDOR_ATTRS: frozenset = frozenset({'src', 'defer', 'nonce'})
_BLOCK_SCRIPTS_RE = re.compile(r'\{%-?\s*block\s+scripts\s*-?%\}')
_ENDBLOCK_RE = re.compile(r'\{%-?\s*endblock(?:\s+scripts)?\s*-?%\}')
_BASE_TEMPLATE: str = 'base/base.html'

# WP3 확장 — 템플릿 URL 속성의 스크립트 스킴 · srcdoc · 태그로 조립한 스킴 · SVG set/animate 의 href
_URL_ATTRS: frozenset = frozenset({'href', 'src', 'action', 'formaction', 'xlink:href', 'data', 'poster',
                                   'background', 'srcset', 'ping', 'cite'})
_ATTR_RE = re.compile(r'''\s([A-Za-z_:][\w:.-]*)\s*=\s*("([^"]*)"|'([^']*)'|([^\s"'=<>`]+))''')
_TAG_RE = re.compile(r'\{\{.*?\}\}|\{%.*?%\}', re.S)
_CTRL_RE = re.compile(r'[\x00-\x20\x7f]')
_PH: str = '\ue000'
_SCHEME_POS_RE = re.compile(r'^[A-Za-z0-9+.\-\ue000]*$')
_SVG_HREF_RE = re.compile(r'<(?:set|animate\w*)\b[^>]*attributeName\s*=\s*["\'](?:xlink:)?href["\']', re.I)


def wp3_url_value(name: str, value: str) -> List[str]:
    """WP3 확장 판정 — URL 속성 값의 스크립트 스킴(엔티티·공백·제어문자 정리 뒤) · srcdoc · 태그로 조립한 스킴."""
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
        self.attrs: list[tuple[str, Optional[str]]] = []

    def handle_starttag(
            self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        if tag.lower() == 'script' and not self.attrs:
            self.attrs = attrs


def _attrs_of(tag: str) -> list[tuple[str, Optional[str]]]:
    parser = _StartTagParser()
    parser.feed(tag)
    return parser.attrs


def _attr_value(attrs: list[tuple[str, Optional[str]]], name: str) -> Optional[str]:
    values = [value for attr_name, value in attrs if attr_name.lower() == name]
    return values[0] if len(values) == 1 else None


def _has_attr(attrs: list[tuple[str, Optional[str]]], name: str) -> bool:
    return any(attr_name.lower() == name for attr_name, _ in attrs)


def _local_static_path(attrs: list[tuple[str, Optional[str]]]) -> tuple[Optional[str], bool]:
    """정확한 `{% static %}` src를 web-상대 파일로 해소한다.

    반환 bool은 신규 표준 `web/` prefix 여부다. 경로의 대소문자는 파일시스템 대조를
    위해 보존한다.
    """
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
    return path == 'base/base.html' or (
        parent_dir_of(path) == 'view' and base_name_of(path).endswith('.html')
    )


def _is_vendor(path: Optional[str]) -> bool:
    return path is not None and path.startswith(VENDOR_DIR + '/')


def _script_path_allowed(ctx: BackstopContext, path: str, standard_prefix: bool) -> bool:
    if path == HTMX_CANONICAL or path == MOTION_JS:
        return standard_prefix
    if _is_vendor(path):
        return standard_prefix and path in ctx.sdk.passed()
    if path in HTMX_LEGACY:
        return path in ctx.base_files
    return standard_prefix and _FEATURE_JS_RE.fullmatch(path) is not None


def _canonical_motion_asset() -> Optional[Path]:
    p: Path = Path(__file__).resolve().parent.parent.parent / 'assets' / 'motion.js'
    return p if p.is_file() else None


def _script_records(ctx: BackstopContext, f: str):
    """템플릿의 script 시작 태그 — (마스킹 본문, [(start, end, tag, attrs, path, standard_prefix)])."""
    ms = ctx.mask_of(f)
    records: List[Tuple[int, int, str, List[Tuple[str, Optional[str]]], Optional[str], bool]] = []
    for start, end, tag in _script_openers(ms.no_comments):
        attrs = _attrs_of(tag)
        path, standard_prefix = _local_static_path(attrs)
        records.append((start, end, tag, attrs, path, standard_prefix))
    return ms, records


def _changed(ctx: BackstopContext, f: str, ms, start: int, end: int) -> bool:
    return any(ctx.line_is_added(f, n) for n in range(ms.line_of(start), ms.line_of(max(start, end - 1)) + 1))


def _block_ranges(text: str) -> List[Tuple[int, int]]:
    ranges: List[Tuple[int, int]] = []
    for m in _BLOCK_SCRIPTS_RE.finditer(text):
        end = _ENDBLOCK_RE.search(text, m.end())
        ranges.append((m.start(), end.end() if end else len(text)))
    return ranges


def _vendor_reasons(ctx: BackstopContext, f: str, ms, records, base_vendor: dict) -> List[Tuple[int, str]]:
    """등재 SDK 로드 태그 규칙(houserules §9 «로드») — ① 속성 ② 페이지 block 밖 ③ 같은 파일 기능 JS 뒤 ④ base block
    여는 줄 뒤 ⑤ base·페이지 중복. ③⑤ 는 벤더 태그나 상대 태그 어느 쪽 줄이 added 여도 낸다. [(start, 사유)]."""
    out: List[Tuple[int, str]] = []
    passed = ctx.sdk.passed()
    text: str = ms.no_comments
    blocks = _block_ranges(text)
    is_base: bool = f == _BASE_TEMPLATE
    features = [(s, e) for s, e, _t, _a, path, std in records
                if path is not None and std and _FEATURE_JS_RE.fullmatch(path)]
    block_lines: bool = any(_changed(ctx, f, ms, m.start(), m.end())
                            for rx in (_BLOCK_SCRIPTS_RE, _ENDBLOCK_RE) for m in rx.finditer(text))
    for start, end, _tag, attrs, path, std in records:
        if not (std and path in passed):
            continue
        changed: bool = _changed(ctx, f, ms, start, end)
        extra = sorted({name.lower() for name, _v in attrs} - _VENDOR_ATTRS - {'async'})   # async 는 공통 사유가 낸다
        if changed and extra:
            out.append((start, '등재 SDK 태그 속성은 src·defer(·CSP nonce)만 — %s · %s' % (', '.join(extra), path)))
        if not is_base and (changed or block_lines) and not any(a <= start < b for a, b in blocks):
            out.append((start, '등재 SDK 태그가 페이지 `{%% block scripts %%}` 밖 — %s' % path))
        before = [(s, e) for s, e in features if s < start]
        if before and (changed or any(_changed(ctx, f, ms, s, e) for s, e in before)):
            out.append((start, '등재 SDK 태그가 같은 파일 기능 JS 태그보다 뒤 — %s' % path))
        if is_base and (changed or block_lines) and any(a < start for a, _b in blocks):
            out.append((start, '등재 SDK 태그가 base 의 `{%% block scripts %%}` 여는 줄보다 뒤 — %s' % path))
        if not is_base and path in base_vendor and (changed or base_vendor[path]):
            out.append((start, 'base·페이지 중복 로드 — %s(base 가 이미 싣는다)' % path))
    return out


def _base_vendor(ctx: BackstopContext) -> dict:
    """base 템플릿이 싣는 등재 SDK 경로 → 그 태그 줄이 added 인가."""
    if _BASE_TEMPLATE not in ctx.files_set or not any(f.startswith(VENDOR_DIR + '/') for f in ctx.files):
        return {}
    ms, records = _script_records(ctx, _BASE_TEMPLATE)
    passed = ctx.sdk.passed()
    found: dict = {}
    for start, end, _tag, _attrs, path, std in records:
        if std and path in passed:
            found[path] = found.get(path, False) or _changed(ctx, _BASE_TEMPLATE, ms, start, end)
    return found


def run_purity(ctx: BackstopContext) -> List[Finding]:
    out: List[Finding] = []
    base_vendor: dict = _base_vendor(ctx)
    vendor_seen: set = set()
    fix_vendor: str = ('등재 SDK 는 `{% static \'web/vendor/<id>/<파일>\' %}` 외부 태그 하나로, 속성 src·defer 만, 그 SDK 를 '
                       '쓰는 페이지의 `{% block scripts %}` 안 기능 JS 태그보다 앞에 둔다(모든 페이지가 쓰면 base 의 '
                       'block 여는 줄 앞 · 중복 금지 — houserules §9).')

    def vendor_findings(f: str, ms, records) -> None:
        for start, reason in _vendor_reasons(ctx, f, ms, records, base_vendor):
            if (f, start, reason) not in vendor_seen:
                vendor_seen.add((f, start, reason))
                out.append(Finding('WP2', f, ms.line_of(start), reason, fix_vendor, '§9'))

    for f in ctx.files:
        ext: str = ext_of(f).lower()

        # ---- WP1: 신규 JS 경로·형태 + core 예약/중복 (§5⑤) · 등재 SDK 사본은 §9
        if ext in ('.js', '.mjs', '.cjs') and ctx.is_added(f):
            is_feature = _FEATURE_JS_RE.fullmatch(f) is not None and f not in HTMX_LEGACY
            if f.startswith(VENDOR_DIR + '/'):
                if f not in ctx.sdk.files().values():
                    out.append(Finding('WP1', f, None,
                        '등재되지 않은 벤더 JS — static/vendor/ 에는 승인·등재된 공식 SDK 사본만 둔다',
                        '공식 SDK 면 G1 승인 뒤 sdk_vendor.py 로 등재하고, 아니면 제3자 JS 를 들이지 않는다(§9).',
                        '§5⑤'))
            elif f in HTMX_LEGACY:
                out.append(Finding('WP1', f, None,
                    'HTMX legacy core 예약 이름 `%s` 신설 — 기존 설치로만 소비 가능' % base_name_of(f),
                    '신규 core는 static/htmx/htmx.min.js 하나만 설치한다.', '§5⑤'))
            elif f not in (HTMX_CANONICAL, MOTION_JS) and not is_feature:
                out.append(Finding('WP1', f, None,
                    '신규 JavaScript 경로·형태 위반 — 기능 파일은 static/js/<기능>.js '
                    'snake_case 평면 한 파일이다',
                    '중첩·다른 폴더·`.min.js`·`.mjs`·`.cjs` 없이 static/js/<기능>.js로 둔다.',
                    '§5⑤'))
            if f in HTMX_ALLOWED and sum(1 for h in HTMX_ALLOWED if h in ctx.files_set) > 1:
                out.append(Finding('WP1', f, None, WP1_CORE_DUPLICATE_REASON,
                    '기존 core를 소비하거나, core가 없을 때만 static/htmx/htmx.min.js를 설치한다.',
                    '§5⑤'))

        # ---- WP5: motion.js 판형 대조 — 플러그인 canonical asset과 byte 동일 (§5⑤)
        if f == MOTION_JS and (ctx.is_added(f) or ctx.is_touched(f)):
            canonical: Optional[Path] = _canonical_motion_asset()
            if canonical is not None:
                have: str = hashlib.sha256((ctx.web / f).read_bytes()).hexdigest()
                want: str = hashlib.sha256(canonical.read_bytes()).hexdigest()
                if have != want:
                    out.append(Finding('WP5', f, None,
                        'motion.js 판형 이탈 — vendored 러너는 플러그인 판형 그대로만 둔다'
                        '(수정·확장 금지)',
                        '플러그인 assets/motion.js를 그대로 재복사한다. 승인된 별도 UI 모션이면 '
                        '기능 JS와 ui-js 처분 좌표로 분리하고 실제 동작을 검증한다.', '§5⑤'))

        # ---- WP2 ⑤ base·페이지 중복: base 태그 줄만 added 여도 페이지 파일에 낸다(교차 파일 색인)
        if (ext == '.html' and not ctx.is_touched(f) and f != _BASE_TEMPLATE
                and any(base_vendor.values()) and _script_location_allowed(f)):
            ms, records = _script_records(ctx, f)
            vendor_findings(f, ms, records)

        if not ctx.is_touched(f):
            continue

        # ---- WP2: 외부 local script의 실제 경로·위치·실행 순서 (§5⑤)
        if ext == '.html':
            ms = ctx.mask_of(f)
            # WP6: Django는 다중줄 {# #}를 주석으로 해석하지 않는다.
            # 유효한 comment 블록은 mask_html이 지운다. verbatim은 의도한 원문 출력이다.
            template_text: str = VERBATIM_RE.sub(
                lambda m: ''.join('\n' if c == '\n' else ' ' for c in m.group()),
                ms.no_comments)
            for m in re.finditer(r'\{#.*?(?:#\}|$)', template_text, re.DOTALL):
                start_line: int = ms.line_of(m.start())
                end_line: int = ms.line_of(max(m.start(), m.end() - 1))
                if any(ctx.line_is_added(f, n) for n in range(start_line, end_line + 1)):
                    out.append(Finding('WP6', f, start_line,
                        'Django 짧은 주석이 닫히지 않았거나 여러 줄이다 — 주석 내용이 응답에 노출된다',
                        '한 줄은 {# … #}, 여러 줄은 {% comment %}…{% endcomment %}를 쓴다. '
                        '실제 렌더 응답도 확인한다.', '§7'))
            ms, script_records = _script_records(ctx, f)
            path_counts: dict[str, int] = {}
            for _s, _e, _t, _a, path, _std in script_records:
                if path is not None:
                    path_counts[path] = path_counts.get(path, 0) + 1

            for start, end, _tag, attrs, path, standard_prefix in script_records:
                start_line = ms.line_of(start)
                if not _changed(ctx, f, ms, start, end):
                    continue
                reason: Optional[str] = None
                vendor_tag: bool = _is_vendor(path) and standard_prefix and path in ctx.sdk.passed()
                if path is None:
                    reason = '실행 script는 실제 src 속성의 정확한 Django static 외부 참조여야 한다'
                elif path not in ctx.files_set:
                    reason = 'script src가 가리키는 로컬 static 파일 없음 — %s' % path
                elif not _script_path_allowed(ctx, path, standard_prefix):
                    reason = 'script src 경로가 허용된 기능 JS/core/motion/등재 SDK 경로가 아니다 — %s' % path
                elif not _script_location_allowed(f):
                    reason = '실행 script 위치 위반 — fragment가 아니라 base 또는 view/ 페이지여야 한다'
                elif _has_attr(attrs, 'async'):
                    reason = '%s — %s' % (WP2_ASYNC_REASON, path)
                else:
                    script_type = (_attr_value(attrs, 'type') or '').strip().lower()
                    if (vendor_tag or script_type != 'module') and not _has_attr(attrs, 'defer'):
                        reason = '%s — %s' % (WP2_DEFER_REASON, path)
                    elif path_counts.get(path, 0) > 1:
                        reason = '같은 페이지/base 템플릿의 script 중복 로드 — %s' % path
                if reason is not None:
                    out.append(Finding('WP2', f, start_line, reason,
                        '실재하는 로컬 파일을 `{% static \'web/…\' %}`로 한 번 참조하고, '
                        'classic은 defer·module은 type="module"을 쓰며 async와 fragment 로드를 제거한다.',
                        '§5⑤'))
            if _script_location_allowed(f) and (base_vendor or any(_is_vendor(r[4]) for r in script_records)):
                vendor_findings(f, ms, script_records)

            # ---- WP3: 인라인 이벤트 핸들러·htmx JS 채널 금지 (§5⑤)
            for m in _ON_ATTR_RE.finditer(ms.no_comments):
                line = ms.line_of(m.start(1))
                if ctx.line_is_added(f, line):
                    out.append(Finding('WP3', f, line,
                        '인라인 이벤트 핸들러 `%s=` — 속성 속 JS도 커스텀 JS다' % m.group(1).strip(),
                        '서버 요청은 HTMX 선언으로, 승인된 브라우저 UI 상호작용은 외부 기능 JS로 옮긴다.',
                        '§5⑤'))
            for m in _HX_JS_VALS_RE.finditer(ms.no_comments):
                line = ms.line_of(m.start())
                if ctx.line_is_added(f, line):
                    out.append(Finding('WP3', f, line,
                        'htmx `js:` 채널 — hx-vals/hx-headers의 `js:` 접두는 htmx가 eval하는 임의 JS다',
                        'hx-vals/hx-headers는 정적 JSON이나 서버가 escape한 데이터만 쓰고 '
                        '승인된 UI 동작은 외부 기능 JS로 분리한다.',
                        '§5⑤'))
            for m in _HX_TRIGGER_COND_RE.finditer(ms.no_comments):
                line = ms.line_of(m.start())
                if ctx.line_is_added(f, line):
                    out.append(Finding('WP3', f, line,
                        'hx-trigger `[조건식]` — 대괄호 이벤트 필터는 htmx가 eval하는 임의 JS다',
                        'hx-trigger는 이벤트 이름만 쓰고 조건은 서버 판정 또는 승인된 외부 UI JS가 소유한다.',
                        '§5⑤'))
            for m in _ATTR_RE.finditer(ms.no_comments):
                name: str = m.group(1).lower()
                if name != 'srcdoc' and name not in _URL_ATTRS:
                    continue
                value: str = next(g for g in (m.group(3), m.group(4), m.group(5)) if g is not None)
                line = ms.line_of(m.start(1))
                if not ctx.line_is_added(f, line):
                    continue
                for reason in wp3_url_value(name, value):
                    out.append(Finding('WP3', f, line, reason,
                        '스크립트는 외부 기능 JS 로만 실행한다 — 링크·폼 주소는 서버가 만든 URL(`{% url %}`·state)만 '
                        '쓰고 스킴을 템플릿 태그로 조립하지 않는다.', '§5⑤'))
            for m in _SVG_HREF_RE.finditer(ms.no_comments):
                line = ms.line_of(m.start())
                if ctx.line_is_added(f, line):
                    out.append(Finding('WP3', f, line,
                        'SVG set/animate 가 href 를 바꾼다 — 링크 주소를 실행 시점에 바꾸는 채널',
                        'SVG 애니메이션으로 href·xlink:href 를 바꾸지 않는다.', '§5⑤'))

        # ---- WP4: 템플릿·CSS 색 리터럴 — tokens.css 자신만 예외 (§4 tokens 행·§8)
        if ext in ('.html', '.css') and f != _TOKENS_CSS:
            ms = ctx.mask_of(f)
            for m in _COLOR_RE.finditer(ms.no_comments):
                line = ms.line_of(m.start())
                if ctx.line_is_added(f, line):
                    out.append(Finding('WP4', f, line,
                        '색 리터럴 `%s` — 시각 값의 단일 출처는 design_system/foundation/tokens.css다'
                        % m.group(0).strip('('),
                        '토큰을 tokens.css에 정의하고 `var(--color-…)`로 참조한다.', '§4'))

    return out
