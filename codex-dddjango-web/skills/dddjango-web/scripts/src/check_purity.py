# WP — 순수성 4종 (값 정본: discipline-web-houserules §5⑤ — D12 «순수 HTML+HTMX+CSS»).
# 게이트: WP1=added 파일, WP2~WP4=touched 파일의 added 줄.
#
# *왜 결정적 백스톱인가*: D12의 위반은 «.js 파일의 존재»·«<script>·on* 속성·색
# 리터럴이라는 토큰의 존재»로 환원된다 — 우회 스크립트는 형태로 막는다.
# (판형: dddart check_pubspec의 «토대 불변식» PJ 패밀리)

import re
from typing import List

from .common import BackstopContext, Finding, HTMX_ALLOWED, ext_of

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

# 색 리터럴 — #hex(3·4·6·8, HTML 엔티티 `&#…;` 제외)·rgb()·hsl() 계열
_COLOR_RE = re.compile(
    r'(?<!&)#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})(?![0-9a-zA-Z_-])'
    r'|\b(?:rgb|rgba|hsl|hsla)\s*\(')

_TOKENS_CSS = 'design_system/foundation/tokens.css'


def run_purity(ctx: BackstopContext) -> List[Finding]:
    out: List[Finding] = []

    for f in ctx.files:
        ext: str = ext_of(f)

        # ---- WP1: .js 신설 금지 — vendored htmx 1파일 예외 (§5⑤ D12)
        if ext == '.js' and ctx.is_added(f):
            if f not in HTMX_ALLOWED:
                out.append(Finding('WP1', f, None,
                    '커스텀 JS 금지 — web의 JS는 vendored htmx 단일(타 라이브러리 vendored 추가도 금지)',
                    '동작은 HTMX 속성과 CSS로 표현한다 — 표현 불가한 동작 요구는 우회 스크립트를 '
                    '짜지 말고 설계로 반송한다.', '§5⑤'))
            elif sum(1 for h in HTMX_ALLOWED if h in ctx.files_set) > 1:
                out.append(Finding('WP1', f, None,
                    'vendored htmx 중복 — JS는 htmx **1파일**이다(htmx.min.js 또는 htmx.js)',
                    '한 파일만 남기고 나머지를 삭제한다.', '§5⑤'))

        if not ctx.is_touched(f):
            continue

        # ---- WP2: 템플릿 inline <script> 금지 (§5⑤ — src로 htmx를 싣는 태그만 예외)
        if ext == '.html':
            ms = ctx.mask_of(f)
            for m in re.finditer(r'<script\b', ms.no_comments, re.IGNORECASE):
                line: int = ms.line_of(m.start())
                if not ctx.line_is_added(f, line):
                    continue
                gt: int = ms.no_comments.find('>', m.start())
                tag: str = ms.no_comments[m.start():gt if gt >= 0 else m.start() + 300].lower()
                if 'src=' in tag.replace(' ', '') and 'htmx' in tag:
                    continue
                out.append(Finding('WP2', f, line,
                    '템플릿 `<script>` — inline JS·타 스크립트 로드 금지(허용은 vendored htmx '
                    'src 로드 태그뿐)',
                    '동작은 HTMX 속성(hx-get·hx-target·hx-swap 류)과 CSS로 표현하고, '
                    '불가하면 설계로 반송한다.', '§5⑤'))

            # ---- WP3: 인라인 이벤트 핸들러 속성 금지 (§5⑤)
            for m in _ON_ATTR_RE.finditer(ms.no_comments):
                line = ms.line_of(m.start(1))
                if ctx.line_is_added(f, line):
                    out.append(Finding('WP3', f, line,
                        '인라인 이벤트 핸들러 `%s=` — 속성 속 JS도 커스텀 JS다' % m.group(1).strip(),
                        '상호작용은 HTMX 선언 속성으로(폼 제출·부분 재렌더), 시각 반응은 CSS로 옮긴다.',
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
