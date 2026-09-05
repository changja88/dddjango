# WP — 순수성·템플릿 출력 6종 (값 정본: discipline-web-houserules §5⑤·§7).
# 게이트: WP1=added 파일, WP2~WP4=touched 파일의 added 줄, WP5=touched·added된 motion.js 전체.
#
# *왜 결정적 백스톱인가*: D12의 위반은 «.js 파일의 존재»·«<script>·on* 속성·js: 채널·색
# 리터럴이라는 토큰의 존재»·«vendored 판형과의 byte 차이»로 환원된다 — 우회 스크립트는
# 형태로 막는다. (판형: dddart check_pubspec의 «토대 불변식» PJ 패밀리)

import hashlib
import re
from pathlib import Path
from typing import List, Optional

from .common import (BackstopContext, Finding, HTMX_ALLOWED, MOTION_JS,
                     VENDORED_JS_ALLOWED, VERBATIM_RE, ext_of)

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

# <script src> 허용 판정 — substring 매칭이 아니라 src 값의 경로 꼬리 정확 대조(CDN 차단)
_SRC_RE = re.compile(r'''src\s*=\s*(?:"([^"]*)"|'([^']*)')''', re.IGNORECASE)
_STATIC_ARG_RE = re.compile(r'''\{%\s*static\s+(?:"([^"]*)"|'([^']*)')''')
_VENDORED_SCRIPT_SUFFIXES = ('js/htmx.min.js', 'js/htmx.js', 'js/motion.js')


def _is_vendored_script_tag(tag: str) -> bool:
    """<script> 태그가 vendored 2종의 정확 경로 로드인가 — src 값(또는 {% static %} 인자)이
    허용 경로 꼬리로 끝나야 한다. 절대 URL(CDN)은 이름에 htmx/motion이 들어도 불허(§5⑤)."""
    m = _SRC_RE.search(tag)
    if not m:
        return False
    val: str = (m.group(1) or m.group(2) or '').strip()
    sm = _STATIC_ARG_RE.search(val)
    if sm:
        val = (sm.group(1) or sm.group(2) or '').strip()
    elif val.startswith(('http://', 'https://', '//')):
        return False
    return val.endswith(_VENDORED_SCRIPT_SUFFIXES)


def _canonical_motion_asset() -> Optional[Path]:
    p: Path = Path(__file__).resolve().parent.parent.parent / 'assets' / 'motion.js'
    return p if p.is_file() else None


def run_purity(ctx: BackstopContext) -> List[Finding]:
    out: List[Finding] = []

    for f in ctx.files:
        ext: str = ext_of(f)

        # ---- WP1: .js 신설 금지 — vendored 닫힌 2그룹 예외 (§5⑤ D12v2)
        if ext == '.js' and ctx.is_added(f):
            if f not in VENDORED_JS_ALLOWED:
                out.append(Finding('WP1', f, None,
                    '커스텀 JS 금지 — web의 JS는 vendored 닫힌 2파일(htmx·motion.js)이다'
                    '(타 라이브러리 vendored 추가도 금지)',
                    '동작은 HTMX 속성·CSS 모션·data-motion 선언으로 표현한다 — 표현 불가한 '
                    '동작 요구는 우회 스크립트를 짜지 말고 설계로 반송한다.', '§5⑤'))
            elif f in HTMX_ALLOWED and sum(1 for h in HTMX_ALLOWED if h in ctx.files_set) > 1:
                out.append(Finding('WP1', f, None,
                    'vendored htmx 중복 — htmx는 **1파일**이다(htmx.min.js 또는 htmx.js)',
                    '한 파일만 남기고 나머지를 삭제한다.', '§5⑤'))

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
                        '플러그인 assets/motion.js를 그대로 재복사한다 — 러너로 안 되는 모션 '
                        '요구는 설계로 반송한다(한계 분류).', '§5⑤'))

        if not ctx.is_touched(f):
            continue

        # ---- WP2: 템플릿 inline <script> 금지 (§5⑤ — vendored 정확 경로 src 태그만 예외)
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
            for m in re.finditer(r'<script\b', ms.no_comments, re.IGNORECASE):
                line: int = ms.line_of(m.start())
                if not ctx.line_is_added(f, line):
                    continue
                gt: int = ms.no_comments.find('>', m.start())
                tag: str = ms.no_comments[m.start():gt if gt >= 0 else m.start() + 300].lower()
                if _is_vendored_script_tag(tag):
                    continue
                out.append(Finding('WP2', f, line,
                    '템플릿 `<script>` — inline JS·타 스크립트 로드 금지(허용은 vendored '
                    'htmx·motion.js의 정확 경로 src 로드 태그뿐 — CDN 불허)',
                    '동작은 HTMX 속성(hx-get·hx-target·hx-swap 류)과 CSS로 표현하고, '
                    '불가하면 설계로 반송한다.', '§5⑤'))

            # ---- WP3: 인라인 이벤트 핸들러·htmx JS 채널 금지 (§5⑤)
            for m in _ON_ATTR_RE.finditer(ms.no_comments):
                line = ms.line_of(m.start(1))
                if ctx.line_is_added(f, line):
                    out.append(Finding('WP3', f, line,
                        '인라인 이벤트 핸들러 `%s=` — 속성 속 JS도 커스텀 JS다' % m.group(1).strip(),
                        '상호작용은 HTMX 선언 속성으로(폼 제출·부분 재렌더), 시각 반응은 CSS로 옮긴다.',
                        '§5⑤'))
            for m in _HX_JS_VALS_RE.finditer(ms.no_comments):
                line = ms.line_of(m.start())
                if ctx.line_is_added(f, line):
                    out.append(Finding('WP3', f, line,
                        'htmx `js:` 채널 — hx-vals/hx-headers의 `js:` 접두는 htmx가 eval하는 임의 JS다',
                        'hx-vals/hx-headers는 정적 JSON만 쓴다 — 동적 값이 필요하면 설계로 반송한다.',
                        '§5⑤'))
            for m in _HX_TRIGGER_COND_RE.finditer(ms.no_comments):
                line = ms.line_of(m.start())
                if ctx.line_is_added(f, line):
                    out.append(Finding('WP3', f, line,
                        'hx-trigger `[조건식]` — 대괄호 이벤트 필터는 htmx가 eval하는 임의 JS다',
                        'hx-trigger는 이벤트 이름만 쓴다 — 조건 분기는 서버 재렌더로 옮긴다.',
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
