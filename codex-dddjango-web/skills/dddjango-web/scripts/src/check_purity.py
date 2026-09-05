# WP — UI 실행 경계·템플릿 출력 6종 (값 정본: discipline-web-houserules §5⑤·§7).
# 게이트: WP1=added 파일, WP2~WP4=touched 파일의 added 줄, WP5=touched·added된 motion.js 전체.
#
# *왜 결정적 백스톱인가*: 파일 경로·실행 태그·인라인 채널·색 리터럴·motion 판형처럼
# 형태로 환원되는 경계만 검사한다. 기능 JS의 업무 의미·기능 일대일·실제 동작은 감수와
# 브라우저 증거가 맡는다. (판형: dddart check_pubspec의 «토대 불변식» PJ 패밀리)

import hashlib
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import List, Optional, Tuple

from .common import (BackstopContext, Finding, HTMX_ALLOWED, HTMX_CANONICAL,
                     HTMX_LEGACY, MOTION_JS, VERBATIM_RE, base_name_of,
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


def _script_path_allowed(ctx: BackstopContext, path: str, standard_prefix: bool) -> bool:
    if path == HTMX_CANONICAL or path == MOTION_JS:
        return standard_prefix
    if path in HTMX_LEGACY:
        return path in ctx.base_files
    return standard_prefix and _FEATURE_JS_RE.fullmatch(path) is not None


def _canonical_motion_asset() -> Optional[Path]:
    p: Path = Path(__file__).resolve().parent.parent.parent / 'assets' / 'motion.js'
    return p if p.is_file() else None


def run_purity(ctx: BackstopContext) -> List[Finding]:
    out: List[Finding] = []

    for f in ctx.files:
        ext: str = ext_of(f)

        # ---- WP1: 신규 JS 경로·형태 + core 예약/중복 (§5⑤)
        if ext in ('.js', '.mjs', '.cjs') and ctx.is_added(f):
            is_feature = _FEATURE_JS_RE.fullmatch(f) is not None and f not in HTMX_LEGACY
            if f in HTMX_LEGACY:
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
                out.append(Finding('WP1', f, None,
                    'HTMX core 중복 — canonical과 legacy 설치를 합쳐 한 파일이어야 한다',
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
            script_records: List[Tuple[int, int, str, List[Tuple[str, Optional[str]]],
                                       Optional[str], bool]] = []
            path_counts: dict[str, int] = {}
            for start, end, tag in _script_openers(ms.no_comments):
                attrs = _attrs_of(tag)
                path, standard_prefix = _local_static_path(attrs)
                script_records.append((start, end, tag, attrs, path, standard_prefix))
                if path is not None:
                    path_counts[path] = path_counts.get(path, 0) + 1

            for start, end, _tag, attrs, path, standard_prefix in script_records:
                start_line: int = ms.line_of(start)
                end_line: int = ms.line_of(max(start, end - 1))
                changed = any(
                    ctx.line_is_added(f, n) for n in range(start_line, end_line + 1)
                )
                if not changed:
                    continue
                reason: Optional[str] = None
                if path is None:
                    reason = '실행 script는 실제 src 속성의 정확한 Django static 외부 참조여야 한다'
                elif path not in ctx.files_set:
                    reason = 'script src가 가리키는 로컬 static 파일 없음 — %s' % path
                elif not _script_path_allowed(ctx, path, standard_prefix):
                    reason = 'script src 경로가 허용된 기능 JS/core/motion 경로가 아니다 — %s' % path
                elif not _script_location_allowed(f):
                    reason = '실행 script 위치 위반 — fragment가 아니라 base 또는 view/ 페이지여야 한다'
                elif _has_attr(attrs, 'async'):
                    reason = 'async 실행 금지 — DOM·의존 순서를 보존한다'
                else:
                    script_type = (_attr_value(attrs, 'type') or '').strip().lower()
                    if script_type != 'module' and not _has_attr(attrs, 'defer'):
                        reason = 'classic 외부 스크립트는 defer가 필요하다'
                    elif path_counts.get(path, 0) > 1:
                        reason = '같은 페이지/base 템플릿의 script 중복 로드 — %s' % path
                if reason is not None:
                    out.append(Finding('WP2', f, start_line, reason,
                        '실재하는 로컬 파일을 `{% static \'web/…\' %}`로 한 번 참조하고, '
                        'classic은 defer·module은 type="module"을 쓰며 async와 fragment 로드를 제거한다.',
                        '§5⑤'))

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
