#!/usr/bin/env python3
# dddjango-web 결정적 백스톱 러너 — 단일 엔트리, 검사 26종 인프로세스 실행.
# (판형: dddart scripts/backstop.dart · 값 정본: discipline-web-houserules §1~§5·§7)
#
# 사용:
#   python backstop.py <대상 프로젝트 루트> [--diff-base <commit>] [--all]
#                      [--only ws,wi,wn,wp|<검사ID>…]
#
# 종료코드: 0=clean / 1=사용·내부 오류(미실행 — 통과가 아니다) / 2=blocker(발견 일괄
# 출력 — fail-fast 금지). (houserules §7 exit 계약)
# 게이트: 구조·명명=added 파일/디렉터리, 격리·순수성=touched 파일의 added 줄,
# 골격 완비=신규 단위 → 레거시 불발화. 비git·기준 부재 시 전역 검사로 퇴화 notice.
# 스크립트는 파이프라인 상태(build-state.json)를 모른다 — 컨텍스트는 전부 인자.

import sys
import traceback
from pathlib import Path
from typing import List, Optional, Set

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.common import BackstopContext, Finding  # noqa: E402
from src.check_structure import run_structure  # noqa: E402
from src.check_imports import run_imports  # noqa: E402
from src.check_naming import run_naming  # noqa: E402
from src.check_purity import run_purity  # noqa: E402

TOTAL_CHECKS: int = 26  # WS8 + WI4 + WN8 + WP6

_USAGE: str = ('사용: python backstop.py <대상 프로젝트 루트> '
               '[--diff-base <commit>] [--all] [--only ws,wi,wn,wp]')


def main(argv: List[str]) -> int:
    target: Optional[str] = None
    diff_base: Optional[str] = None
    all_mode: bool = False
    only: Set[str] = set()

    i: int = 0
    while i < len(argv):
        a: str = argv[i]
        if a == '--diff-base':
            i += 1
            if i >= len(argv):
                print('[backstop] 사용 오류: --diff-base 값 없음', file=sys.stderr)
                return 1
            diff_base = argv[i]
        elif a == '--all':
            all_mode = True
        elif a == '--only':
            i += 1
            if i >= len(argv):
                print('[backstop] 사용 오류: --only 값 없음', file=sys.stderr)
                return 1
            only.update(s.strip().lower() for s in argv[i].split(',') if s.strip())
        elif a.startswith('--'):
            print('[backstop] 사용 오류: 알 수 없는 옵션 %s' % a, file=sys.stderr)
            return 1
        else:
            target = a
        i += 1

    if target is None:
        print(_USAGE, file=sys.stderr)
        return 1
    root: Path = Path(target)
    if not root.is_dir():
        print('[backstop] 사용 오류: 디렉터리 아님 — %s' % target, file=sys.stderr)
        return 1

    def family_on(fam: str) -> bool:
        return (not only) or fam in only or any(o.startswith(fam) and len(o) > 2 for o in only)

    def id_on(check_id: str) -> bool:
        if not only:
            return True
        l: str = check_id.lower()
        return l in only or l[:2] in only

    ctx: BackstopContext = BackstopContext.build(root=root, diff_base=diff_base,
                                                 all_mode=all_mode)

    if not ctx.git_repo:
        ctx.notices.append('[info] git 저장소 아님 — 게이트 불가, 전역 검사로 퇴화'
                           '(레거시 발견 폭주 가능). 파이프라인 경로는 git 프로젝트에서 '
                           'Phase 2 진입 스냅샷을 주입한다(houserules §7).')
    elif diff_base is None and not all_mode:
        ctx.notices.append('[info] --diff-base 없음 — 게이트 불가, 전역 검사로 퇴화. '
                           '파이프라인 호출은 Phase 2 진입 스냅샷(git_snapshot)을 '
                           '주입한다(houserules §7).')

    findings: List[Finding] = []
    try:
        if family_on('ws'):
            findings.extend(run_structure(ctx))
        if family_on('wi'):
            findings.extend(run_imports(ctx))
        if family_on('wn'):
            findings.extend(run_naming(ctx))
        if family_on('wp'):
            findings.extend(run_purity(ctx))
    except Exception:
        print('[backstop] 내부 오류:\n%s' % traceback.format_exc(), file=sys.stderr)
        return 1

    shown: List[Finding] = sorted(
        (f for f in findings if id_on(f.check_id)),
        key=lambda f: (f.check_id, f.path, f.line or 0))

    for n in ctx.notices:
        print(n)
    if ctx.notices:
        print()
    for f in shown:
        print(f)
        print()
    if ctx.gated and diff_base is not None:
        mode: str = 'gated(diff-base %s)' % diff_base[:8]
    elif all_mode:
        mode = 'all'
    else:
        mode = '전역 퇴화'
    print('[backstop] 검사 %d종(%s) — blocker %d건' % (TOTAL_CHECKS, mode, len(shown)))
    return 0 if not shown else 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
