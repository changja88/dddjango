# WI — 격리 4종 (값 정본: discipline-web-houserules §5 ①~④ 기계 판별 가능부).
# 게이트: touched 파일의 added 줄 (레거시 파일의 기존 위반에 불발화).
#
# *왜 결정적 백스톱인가*: 두 세계(web ↔ 백엔드)의 계약은 URL+JSON뿐이다 —
# import 한 줄·URL 리터럴 한 조각이 곧 위반이라는 기계적 사실로 환원된다.
# 주석·문자열 마스킹으로 교정 주석 속 토큰의 재발화를 차단한다. (판형: dddart check_imports)

import re
from typing import List, Set

from .common import (
    BACKEND_TOP_PKGS, BackstopContext, Finding, ImportEdge, ext_of, segs_of,
)

# §5④ 휴리스틱 — 템플릿 루트상대 URL 하드코딩(외부 링크 `//`·`http(s)`는 비대상)
_HARD_URL_RE = re.compile(
    r'''\b(href|action|hx-get|hx-post|hx-put|hx-patch|hx-delete)\s*=\s*["']\s*/(?!/)''',
    re.IGNORECASE)


def run_imports(ctx: BackstopContext) -> List[Finding]:
    out: List[Finding] = []
    deny: Set[str] = BACKEND_TOP_PKGS | ctx.project_pkgs

    for f in ctx.files:
        if not ctx.is_touched(f):
            continue
        ext: str = ext_of(f)
        in_client: bool = segs_of(f)[0] == 'client'

        if ext == '.py':
            for e in ctx.edges_of(f):
                if not ctx.line_is_added(f, e.line):
                    continue
                _wi1(out, f, e, deny)
                if not in_client:
                    _wi2(out, f, e)

        if ext in ('.py', '.html') and not in_client:
            # ---- WI3: client 밖 `/api/` 경로 리터럴 금지 (§5④ — BC API URL의 유일
            # 거처는 그 계약의 client 모듈이다)
            ms = ctx.mask_of(f)
            for m in re.finditer(r'/api/', ms.no_comments):
                line: int = ms.line_of(m.start())
                if ctx.line_is_added(f, line):
                    out.append(Finding('WI3', f, line,
                        'client 밖 API URL 리터럴 `/api/…` — BC API URL의 유일 거처는 client 모듈이다',
                        'URL 문자열을 그 계약의 client/<bc>/<capability>_client.py로 옮기고, '
                        '여기서는 client 호출만 남긴다.', '§5④'))

        if ext == '.html':
            # ---- WI4: 템플릿 하드코딩 URL — {% url %} 강제 (§5④)
            ms = ctx.mask_of(f)
            for m in _HARD_URL_RE.finditer(ms.no_comments):
                line = ms.line_of(m.start())
                if ctx.line_is_added(f, line):
                    out.append(Finding('WI4', f, line,
                        '템플릿 하드코딩 URL `%s="/…"` — 라우트 리터럴의 거처는 urls.py뿐' % m.group(1),
                        "`{% url '<name>' %}`(정적 자산은 `{% static %}`)로 이름만 참조한다.",
                        '§5④'))

    return out


def _wi1(out: List[Finding], f: str, e: ImportEdge, deny: Set[str]) -> None:
    """WI1 — web/**에서 `application.`·`framework.`·<project 패키지> import 0 (§5①)."""
    for cand in e.candidates:
        if cand and cand[0] in deny:
            out.append(Finding('WI1', f, e.line,
                'web에서 백엔드 내부 `%s` import — 두 세계의 계약은 URL+JSON뿐이다(D5·D7)'
                % '.'.join(cand[:2] if len(cand) > 1 else cand),
                'import를 지우고 실물 API 계약을 client/<bc>/로 소비한다 — 필요한 API가 '
                '없으면 web에서 가정하지 말고 «/dddjango로 발주»를 안내한다.', '§5①'))
            return  # 간선당 1건


def _wi2(out: List[Finding], f: str, e: ImportEdge) -> None:
    """WI2 — API 호출 표면(django.test Client·requests·urllib.request)은 client/ 전속 (§5②)."""
    mp = e.module
    if mp is None or not mp:
        return
    surface: str = ''
    if mp[0] == 'requests':
        surface = 'requests'
    elif mp[:2] == ['urllib', 'request'] or (mp == ['urllib'] and 'request' in e.names):
        surface = 'urllib.request'
    elif mp[:2] == ['django', 'test'] or (mp == ['django'] and 'test' in e.names):
        surface = 'django.test'
    if surface:
        out.append(Finding('WI2', f, e.line,
            'client 밖 API 호출 표면 `%s` import — HTTP 호출은 client/ 전속이다' % surface,
            'view·VM·템플릿은 HTTP를 모른다 — 호출 코드를 client/<bc>/<capability>_client.py로 '
            '옮기고 VM이 client를 호출하게 한다.', '§5②'))
