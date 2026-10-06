#!/usr/bin/env python3
# dddjango-web 결정적 백스톱 러너 — 단일 엔트리, 검사 84종 인프로세스 실행.
# (판형: dddart scripts/backstop.dart — 같은 인자·같은 종료 코드·같은 게이트)
#
# 사용:
#   python3 backstop.py <대상 프로젝트 루트> [--diff-base <commit>] [--all] [--slice-end]
#                       [--only st,im,nm,cy,tg,pj,md,pu,wv|<검사ID>…] [--update-baseline]
#                       [--design-build <산출물 폴더>]
#   python3 backstop.py <대상 프로젝트 루트> --debt-scan [--refactor] [--json <경로>]
#   python3 backstop.py <대상 프로젝트 루트> --debt-residual <.dddjango-web/<산출물 폴더>>
#   python3 backstop.py <대상 프로젝트 루트> --subst-check <기준 커밋> <대상 커밋>
#                       [--names <design-spec.md>] [--except <web/ 밖 비테스트 경로>]… [--build <산출물 폴더>]
#
# 종료코드: 0=clean / 1=사용·내부 오류·판정 불가(미실행 — 통과가 아니다) / 2=blocker(발견 일괄 출력 — fail-fast 금지).
# 게이트: 구조·명명=added, import=touched의 added 줄, 골격=신규 단위, 순환=전역+베이스라인
# (.dddjango-web/backstop-baseline.json). 참조 = Python import(함수 안 포함) + 템플릿 extends·include·static
# + CSS @import·url() — 조각 CSS(static/application/·static/root/)는 소유자의 presentation 자리로 센다.
# 스크립트는 파이프라인 상태(build-state.json)를 모른다 — 컨텍스트는 전부 인자(--design-build · --build 가 주는 폴더만 읽는다).
#
# 슬라이스 끝 실행(--slice-end — Phase 2 에서 슬라이스 커밋 앞): 뒤 슬라이스가 채울 검사(SLICE_END_DEFERRED)를 미룬다 —
#   그 발견을 내지 않고 CY 는 돌지도 않는다(순환 기준선 파일을 만들지 않는다). 미룬 검사는 G2 직전 실행(인자 없음)이 본다.
#   --update-baseline · --only · 러너 모드와 함께 쓰지 않는다.
# 러너 모드(검사 ID 가 아니다 — v1.3.1 그대로):
#   빚 모드(src/debt.py — Phase 0 step 4′ · G2): --debt-scan 은 web/ 전체의 기존 위반(빚)을 키 (검사, 경로)로
#   동결하고(ST·MD·IM·NM·PU·WV), --debt-residual 은 G0 절의 ⓐ·요구 키 잔존을 센다. --refactor 는 --debt-scan 전용.
#   치환 확인(src/subst.py — 슬라이스 0 끝 green ④): --subst-check 는 기준..대상 사이 web/ 밖 레인 편집이 슬라이스 0 의
#   테스트 치환뿐인지 본다(--names·--except·--build 는 그 전용).
#   모드끼리, 그리고 --diff-base·--all·--only·--design-build·--update-baseline 과 함께 쓰지 않는다.
#
# 검사 84종 (dddart 번호 그대로 · 옮길 수 없는 번호는 비움 · 새 검사는 패밀리 끝 번호 뒤):
#   ST 13 — ST0~ST11(dddart) + ST12(web/static/ 트리 — application·root·js·htmx·vendor·images·fonts)
#   IM 27 — IM1~IM23(dddart) + IM24(상대 import) · IM25(백엔드 import) · IM26(extends 대상) · IM27(HTTP 표면·API URL 리터럴)
#   NM 19 — NM1~NM6 · NM8(common 상태 동작 proxy — common @riverpod 자리) · NM9~NM17(dddart)
#           + NM18(view 짝) · NM19(조각 CSS 짝 — BC·root) · NM20(snake_case) · NM7 비움(@riverpod 허용 위치)
#   CY 1  — CY1
#   TG 1  — TG1(web_test/ 미러)
#   MD 2  — MD1(frozen dataclass 형태) · MD2(from_json 형태)
#   PJ 2  — PJ1(pytest·pytest-django 선언) · PJ2(htmx core 단일 고정 판) · PJ3 비움(2.1.0 — vendor 는 공식 SDK 등재 절차 WV)
#   PU 6  — PU1 · PU2 · PU3 · PU6(v1.3.1 WP 번호 그대로) + PU7(자동 이스케이프 우회) · PU8(JS 동적 실행)
#           · PU4 비움(색 리터럴 → NM10) · PU5 비움(motion.js 판형 — 러너 없음)
#   WV 13 — WV1~WV13(공식 SDK 등재 — src/check_vendor.py · v1.3.1 번호 그대로)
#   (RV·HV 는 옮기지 않는다 — riverpod·hive 없음)

from __future__ import annotations

import sys
import traceback
from pathlib import Path
from typing import List, Optional, Set

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.common import CORE_CHECK_IDS, CORE_FAMILIES, BackstopContext, Finding  # noqa: E402
from src.check_cycles import run_cycles  # noqa: E402
from src.check_imports import run_imports  # noqa: E402
from src.check_models import run_models  # noqa: E402
from src.check_naming import run_naming  # noqa: E402
from src.check_project import run_project  # noqa: E402
from src.check_purity import run_purity  # noqa: E402
from src.check_structure import run_structure  # noqa: E402
from src.check_tests import run_tests  # noqa: E402
from src.check_vendor import VENDOR_CHECK_IDS, VendorUndecidable, run_vendor  # noqa: E402
from src.debt import cli_residual, cli_scan  # noqa: E402
from src.subst import cli_subst_check  # noqa: E402

FAMILIES: List[str] = list(CORE_FAMILIES) + ['wv']
CHECK_IDS: List[str] = list(CORE_CHECK_IDS) + list(VENDOR_CHECK_IDS)
TOTAL_CHECKS: int = len(CHECK_IDS)  # 84 = ST13 + IM27 + NM19 + CY1 + TG1 + MD2 + PJ2 + PU6 + WV13
# 슬라이스 끝(--slice-end)에 미루는 검사 — 짝 · 골격 · 미러 · 순환은 뒤 슬라이스가 채운다(G2 직전 실행이 본다 · 이 목록이 단일 출처)
SLICE_END_DEFERRED: List[str] = ['CY1', 'NM4', 'NM5', 'NM18', 'NM19', 'ST4', 'TG1']

_USAGE: str = ('사용: python3 backstop.py <대상 프로젝트 루트> '
               '[--diff-base <commit>] [--all] [--slice-end] [--only st,md,im,nm,cy,tg,pj,pu,wv] [--update-baseline] '
               '[--design-build <폴더>] | --debt-scan [--refactor] [--json <경로>] | --debt-residual <폴더> | '
               '--subst-check <기준> <대상> [--names <명세>] [--except <경로>]… [--build <폴더>]')


def main(argv: List[str]) -> int:
    target: Optional[str] = None
    diff_base: Optional[str] = None
    all_mode: bool = False
    slice_end: bool = False
    update_baseline: bool = False
    only: Set[str] = set()
    design_build: Optional[str] = None
    debt_scan: bool = False
    debt_residual: Optional[str] = None
    json_path: Optional[str] = None
    refactor: bool = False
    subst: Optional[List[str]] = None
    names: Optional[str] = None
    excepts: List[str] = []
    build: Optional[str] = None

    valued = ('--diff-base', '--only', '--design-build', '--json', '--debt-residual', '--names', '--except', '--build')
    i: int = 0
    while i < len(argv):
        a: str = argv[i]
        if a in valued:
            if i + 1 >= len(argv):
                print('[backstop] 사용 오류: %s 값 없음' % a, file=sys.stderr)
                return 1
            value: str = argv[i + 1]
            if a == '--diff-base':
                diff_base = value
            elif a == '--only':
                only.update(s.strip().lower() for s in value.split(',') if s.strip())
            elif a == '--design-build':
                design_build = value
            elif a == '--json':
                json_path = value
            elif a == '--debt-residual':
                debt_residual = value
            elif a == '--names':
                names = value
            elif a == '--build':
                build = value
            else:
                excepts.append(value)
            i += 2
            continue
        if a == '--subst-check':
            if i + 2 >= len(argv) or argv[i + 1].startswith('--') or argv[i + 2].startswith('--'):
                print('[backstop] 사용 오류: --subst-check 값 둘(기준 커밋 · 대상 커밋) 필요', file=sys.stderr)
                return 1
            subst = [argv[i + 1], argv[i + 2]]
            i += 3
            continue
        if a == '--all':
            all_mode = True
        elif a == '--slice-end':
            slice_end = True
        elif a == '--update-baseline':
            update_baseline = True
        elif a == '--debt-scan':
            debt_scan = True
        elif a == '--refactor':
            refactor = True
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

    # ---- 러너 모드(단독) — 빚 스캔 · 빚 잔존 · 치환 확인
    gate_flags: bool = (diff_base is not None or all_mode or bool(only) or design_build is not None
                        or update_baseline or slice_end)
    if subst is not None or names is not None or excepts or build is not None:
        if (subst is None or gate_flags or debt_scan or debt_residual is not None
                or json_path is not None or refactor):
            print('[backstop] 사용 오류: --subst-check 는 단독 모드다 — --debt-scan·--debt-residual·'
                  '--json·--refactor·--diff-base·--all·--only·--design-build·--update-baseline 와 함께 쓰지 않는다'
                  '(--names·--except·--build 는 --subst-check 전용)', file=sys.stderr)
            return 1
        return cli_subst_check(root, subst[0], subst[1], names, excepts, build)
    if debt_scan or debt_residual is not None or json_path is not None or refactor:
        if (debt_scan == (debt_residual is not None) or gate_flags
                or (json_path is not None and not debt_scan) or (refactor and not debt_scan)):
            print('[backstop] 사용 오류: --debt-scan·--debt-residual 은 단독 모드다 — '
                  '서로, 그리고 --diff-base·--all·--only·--design-build·--update-baseline 와 함께 쓰지 않는다'
                  '(--json·--refactor 는 --debt-scan 전용)', file=sys.stderr)
            return 1
        return cli_scan(root, json_path, refactor) if debt_scan else cli_residual(root, debt_residual)

    # ---- 게이트 모드
    if slice_end and (update_baseline or only):
        print('[backstop] 사용 오류: --slice-end 는 --update-baseline·--only 와 함께 쓰지 않는다'
              '(슬라이스 끝 실행은 기준선을 건드리지 않고 미룰 검사를 스스로 정한다)', file=sys.stderr)
        return 1

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
        if family_on('cy') and not slice_end:
            findings.extend(run_cycles(ctx, update_baseline))
        if family_on('tg'):
            findings.extend(run_tests(ctx))
        if family_on('pj'):
            findings.extend(run_project(ctx))
        if family_on('pu'):
            findings.extend(run_purity(ctx))
        if family_on('wv'):
            findings.extend(run_vendor(ctx, design_build=design_build))
    except VendorUndecidable as error:
        print('[backstop] 판정 불가 — %s' % error)
        return 1
    except Exception:  # noqa: BLE001 — 내부 오류는 미실행(통과 아님)으로 exit 1
        print('[backstop] 내부 오류:\n%s' % traceback.format_exc(), file=sys.stderr)
        return 1

    shown: List[Finding] = sorted((f for f in findings if id_on(f.check_id)
                                  and (not slice_end or f.check_id not in SLICE_END_DEFERRED)),
                                  key=lambda f: (f.check_id, f.path, f.line or 0))
    for n in ctx.notices:
        print(n)
    if ctx.notices:
        print('')
    for f in shown:
        print(f)
        print('')
    mode: str = ('gated(diff-base %s)' % diff_base[:8]) if ctx.gated and diff_base else ('all' if all_mode else '전역 퇴화')
    if slice_end:
        print('[backstop] 검사 %d종 중 %d종(슬라이스 끝 — 미룸 %d: %s · %s) — blocker %d건'
              % (TOTAL_CHECKS, TOTAL_CHECKS - len(SLICE_END_DEFERRED), len(SLICE_END_DEFERRED),
                 ' · '.join(SLICE_END_DEFERRED), mode, len(shown)))
    else:
        print('[backstop] 검사 %d종(%s) — blocker %d건' % (TOTAL_CHECKS, mode, len(shown)))
    return 0 if not shown else 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
