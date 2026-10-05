#!/usr/bin/env python3
# dddjango-web 결정적 백스톱 러너 — 단일 엔트리, 검사 72종 인프로세스 실행.
# (판형: dddart scripts/backstop.dart — 같은 인자·같은 종료 코드·같은 게이트)
#
# 사용:
#   python3 backstop.py <대상 프로젝트 루트> [--diff-base <commit>] [--all]
#                       [--only st,im,nm,cy,tg,pj,md,pu|<검사ID>…] [--update-baseline]
#
# 종료코드: 0=clean / 1=사용·내부 오류 / 2=blocker(발견 일괄 출력 — fail-fast 금지).
# 게이트: 구조·명명=added, import=touched의 added 줄, 골격=신규 단위, 순환=전역+베이스라인
# (.dddjango-web/backstop-baseline.json). 참조 = Python import(함수 안 포함) + 템플릿 extends·include·static
# + CSS @import·url() — 조각 CSS(static/application/·static/root/)는 소유자의 presentation 자리로 센다.
# 스크립트는 파이프라인 상태(build-state.json)를 모른다 — 컨텍스트는 전부 인자.
#
# 검사 72종 (dddart 번호 그대로 · 옮길 수 없는 번호는 비움 · 새 검사는 패밀리 끝 번호 뒤):
#   ST 13 — ST0~ST11(dddart) + ST12(web/static/ 트리 — application·root·js·htmx·vendor·images·fonts)
#   IM 27 — IM1~IM23(dddart) + IM24(상대 import) · IM25(백엔드 import) · IM26(extends 대상) · IM27(HTTP 표면·API URL 리터럴)
#   NM 19 — NM1~NM6 · NM8(common 상태 동작 proxy — common @riverpod 자리) · NM9~NM17(dddart)
#           + NM18(view 짝) · NM19(조각 CSS 짝 — BC·root) · NM20(snake_case) · NM7 비움(@riverpod 허용 위치)
#   CY 1  — CY1
#   TG 1  — TG1(web_test/ 미러)
#   MD 2  — MD1(frozen dataclass 형태) · MD2(from_json 형태)
#   PJ 3  — PJ1(pytest·pytest-django 선언) · PJ2(htmx core 단일 고정 판) · PJ3(vendor 버전 고정 사본)
#   PU 6  — PU1 · PU2 · PU3 · PU6(v1.3.1 WP 번호 그대로) + PU7(자동 이스케이프 우회) · PU8(JS 동적 실행)
#           · PU4 비움(색 리터럴 → NM10) · PU5 비움(motion.js 판형 — 러너 없음)
#   (RV·HV 는 옮기지 않는다 — riverpod·hive 없음)

from __future__ import annotations

import sys
import traceback
from pathlib import Path
from typing import List, Optional, Set

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.common import BackstopContext, Finding  # noqa: E402
from src.check_cycles import run_cycles  # noqa: E402
from src.check_imports import run_imports  # noqa: E402
from src.check_models import run_models  # noqa: E402
from src.check_naming import run_naming  # noqa: E402
from src.check_project import run_project  # noqa: E402
from src.check_purity import run_purity  # noqa: E402
from src.check_structure import run_structure  # noqa: E402
from src.check_tests import run_tests  # noqa: E402

FAMILIES: List[str] = ['st', 'md', 'im', 'nm', 'cy', 'tg', 'pj', 'pu']
CHECK_IDS: List[str] = (
    ['ST%d' % n for n in range(0, 13)]                                  # ST0~ST12
    + ['IM%d' % n for n in range(1, 28)]                                # IM1~IM27
    + ['NM%d' % n for n in range(1, 21) if n != 7]                      # NM1~NM20 · NM7 비움
    + ['CY1', 'TG1', 'MD1', 'MD2', 'PJ1', 'PJ2', 'PJ3']
    + ['PU1', 'PU2', 'PU3', 'PU6', 'PU7', 'PU8'])                       # PU4·PU5 비움
TOTAL_CHECKS: int = len(CHECK_IDS)  # 72 = ST13 + IM27 + NM19 + CY1 + TG1 + MD2 + PJ3 + PU6

_USAGE: str = ('사용: python3 backstop.py <대상 프로젝트 루트> '
               '[--diff-base <commit>] [--all] [--only st,md,im,nm,cy,tg,pj,pu] [--update-baseline]')


def main(argv: List[str]) -> int:
    target: Optional[str] = None
    diff_base: Optional[str] = None
    all_mode: bool = False
    update_baseline: bool = False
    only: Set[str] = set()

    i: int = 0
    while i < len(argv):
        a: str = argv[i]
        if a in ('--diff-base', '--only'):
            if i + 1 >= len(argv):
                print('[backstop] 사용 오류: %s 값 없음' % a, file=sys.stderr)
                return 1
            if a == '--diff-base':
                diff_base = argv[i + 1]
            else:
                only.update(s.strip().lower() for s in argv[i + 1].split(',') if s.strip())
            i += 2
            continue
        if a == '--all':
            all_mode = True
        elif a == '--update-baseline':
            update_baseline = True
        elif a.startswith('--'):
            print('[backstop] 사용 오류: 알 수 없는 옵션 %s' % a, file=sys.stderr)
            return 1
        else:
            target = a
        i += 1
    if target is None:
        print(_USAGE, file=sys.stderr)
        return 1
    known: Set[str] = set(FAMILIES) | {c.lower() for c in CHECK_IDS}
    unknown: List[str] = sorted(only - known)
    if unknown:  # 없는 패밀리·검사 ID 를 조용히 0건으로 통과시키지 않는다
        print('[backstop] 사용 오류: 알 수 없는 --only 값 %s — 패밀리 %s 또는 검사 ID(예 st4·im5)'
              % (', '.join(unknown), ','.join(FAMILIES)), file=sys.stderr)
        return 1

    root: Path = Path(target)
    if not root.is_dir():
        print('[backstop] 사용 오류: 디렉터리 아님 — %s' % target, file=sys.stderr)
        return 1
    root = root.resolve()

    def family_on(fam: str) -> bool:
        return not only or fam in only or any(o.startswith(fam) and len(o) > 2 for o in only)

    def id_on(cid: str) -> bool:
        if not only:
            return True
        low: str = cid.lower()
        return low in only or low[:2] in only

    ctx: BackstopContext = BackstopContext.build(root, diff_base, all_mode)

    if not ctx.git_repo:
        ctx.notices.append('[info] git 저장소 아님 — 게이트 불가, 전역 검사로 퇴화(레거시 발견 폭주 가능). '
                           'G0의 git init+초기 커밋 제안이 정답 경로.')
    elif diff_base is None and not all_mode:
        ctx.notices.append('[info] --diff-base 없음 — 게이트 불가, 전역 검사로 퇴화. '
                           '파이프라인 호출은 Phase 2 진입 스냅샷을 주입한다.')

    findings: List[Finding] = []
    try:
        if family_on('st'):
            findings.extend(run_structure(ctx))
        if family_on('md'):
            findings.extend(run_models(ctx))
        if family_on('im'):
            findings.extend(run_imports(ctx))
        if family_on('nm'):
            findings.extend(run_naming(ctx))
        if family_on('cy'):
            findings.extend(run_cycles(ctx, update_baseline))
        if family_on('tg'):
            findings.extend(run_tests(ctx))
        if family_on('pj'):
            findings.extend(run_project(ctx))
        if family_on('pu'):
            findings.extend(run_purity(ctx))
    except Exception:  # noqa: BLE001 — 내부 오류는 미실행(통과 아님)으로 exit 1
        print('[backstop] 내부 오류:\n%s' % traceback.format_exc(), file=sys.stderr)
        return 1

    shown: List[Finding] = sorted((f for f in findings if id_on(f.check_id)),
                                  key=lambda f: (f.check_id, f.path, f.line or 0))
    for n in ctx.notices:
        print(n)
    if ctx.notices:
        print('')
    for f in shown:
        print(f)
        print('')
    mode: str = ('gated(diff-base %s)' % diff_base[:8]) if ctx.gated and diff_base else ('all' if all_mode else '전역 퇴화')
    print('[backstop] 검사 %d종(%s) — blocker %d건' % (TOTAL_CHECKS, mode, len(shown)))
    return 0 if not shown else 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
