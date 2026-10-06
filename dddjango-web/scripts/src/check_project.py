# PJ — web 토대 어설션 2종 (PJ1·PJ2 · PJ3 비움). 게이트: 입력 불변식(시나리오 무관·항상).
#
# *왜 결정적 백스톱인가*: 테스트 도구 선언(pytest·pytest-django) · htmx core 단일 고정 판은
# 어느 입력에도 불변인 토대 사실이며, 그 부재는 «테스트가 돌지 않는 green»·«두 htmx 가 섞인 화면»의 토대다.
# 거짓양성 가드: PJ1은 web_test/ 에 테스트가 *있을 때만*, PJ2는 *새로 더한* htmx core 가 있을 때만 발화.
# PJ3(vendor/<라이브러리>/<버전>/ 고정 사본 · 2.0.0)은 비운다 — 2.1.0 부터 외부 JS 는 G1 승인·등재된 공식 SDK
# 사본(static/vendor/<sdk_id>/<파일>)뿐이고 그 자리·바이트는 WV(src/check_vendor.py)·ST12 vendor 분기가 본다.
# (판형: dddart check_pubspec.dart — riverpod 토대 자리를 web 토대로)

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Set

from .common import HTMX_CORE, HTMX_VERSION, BackstopContext, Finding, segs_of

_RULE_PJ: str = '토대 규약 — pytest·pytest-django 선언 · htmx core 단일 고정 판'
_DECL_FILES = ('requirements*.txt', 'requirements/*.txt', 'pyproject.toml', 'Pipfile', 'setup.cfg', 'setup.py')
_NAME_RE = re.compile(r'''(?<![\w.\-])["']?([A-Za-z][A-Za-z0-9_.\-]*)\s*(?:\[[^\]\n]*\])?\s*(?:==|>=|<=|~=|!=|===|>|<|=|$|["',;\s])''')
_HTMX_VERSION_RE = re.compile(r'''version\s*:\s*["'](\d+\.\d+\.\d+[^"']*)["']''')


def _declared(root: Path) -> Set[str]:
    """의존성 선언 파일들의 패키지 이름(소문자·`_`→`-`) — 외부 의존 0의 경량 토큰 파싱."""
    names: Set[str] = set()
    for pattern in _DECL_FILES:
        for p in root.glob(pattern):
            if not p.is_file():
                continue
            for raw in p.read_text(encoding='utf-8', errors='replace').splitlines():
                line: str = raw.split('#', 1)[0]
                for m in _NAME_RE.finditer(line):
                    names.add(m.group(1).lower().replace('_', '-'))
    return names


def run_project(ctx: BackstopContext) -> List[Finding]:
    out: List[Finding] = []

    # ---- PJ1: 테스트 도구 선언(pytest · pytest-django) — web_test/ 에 테스트가 있을 때만
    test_root: Path = ctx.root / 'web_test'
    if test_root.is_dir() and any(p.is_file() for p in test_root.rglob('*_test.py')):
        missing: List[str] = sorted({'pytest', 'pytest-django'} - _declared(ctx.root))
        if missing:
            out.append(Finding('PJ1', 'web_test/', None,
                'web_test/ 테스트가 있으나 의존성 선언에 %s 없음 — 테스트 도구 토대 부재(pytest web_test 가 돌지 않는다)'
                % ', '.join(missing), _RULE_PJ,
                '호스트 requirements(또는 pyproject)에 버전 고정으로 추가한다 — 예 `pytest-django==<실버전>`.',
                root_rel=True))

    # ---- PJ2: htmx core 단일 설치 · 고정 판 — 새로 더한(added) core 만 본다(브라운필드 기존 core 는 판이 달라도 불발화)
    cores: List[str] = sorted(f for f in ctx.all_files if _is_htmx_core(f))
    new_cores: List[str] = [f for f in cores if ctx.is_added(f)]
    if new_cores and len(cores) > 1:
        out.append(Finding('PJ2', new_cores[0], None,
            'htmx core 이중 설치 — %s' % ' · '.join(cores), _RULE_PJ,
            '기존 core(static/js/htmx*.js)가 있으면 그것만 소비하고, 없을 때만 `%s` 하나를 둔다.' % HTMX_CORE))
    if HTMX_CORE in new_cores:
        m = _HTMX_VERSION_RE.search((ctx.web / HTMX_CORE).read_text(encoding='utf-8', errors='replace'))
        if m and m.group(1) != HTMX_VERSION:
            out.append(Finding('PJ2', HTMX_CORE, None,
                'htmx core 판 `%s` — 고정 판은 %s' % (m.group(1), HTMX_VERSION), _RULE_PJ,
                '`curl -fsSL https://unpkg.com/htmx.org@%s/dist/htmx.min.js` 로 고정 판을 받는다.' % HTMX_VERSION))
    return out


def _is_htmx_core(f: str) -> bool:
    """htmx core 설치 자리 — 고정 판 자리 · 브라운필드 static/js/ · vendor 사본."""
    s: List[str] = segs_of(f)
    core_names = ('htmx.js', 'htmx.min.js')
    if f == HTMX_CORE or (len(s) == 3 and s[:2] == ['static', 'htmx'] and s[2].endswith('.js')):
        return True
    if len(s) == 3 and s[:2] == ['static', 'js'] and s[2] in core_names:
        return True
    return len(s) >= 4 and s[:2] == ['static', 'vendor'] and s[2].startswith('htmx') and s[-1] in core_names
