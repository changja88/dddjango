#!/usr/bin/env python3
"""전수 fixture 실측표 — 검사기 × 위반 fixture × 기대/실측 exit (5번 계획 Phase 4-3).

「백스톱 실측 0」(5차 리뷰 최대 발견)의 종결 장치: 검사기마다 자기 위반
fixture 에서 exit 2 가 나는지를 전수로 실측하고 표로 남긴다. eval v5 는
FROZEN 이므로 실측은 이 fixture 결정 레인만 쓴다.

케이스: skeleton 5 + 기존 15종×2 + API-error 3종×2(--error-profile auto)
       + 신설 8종×2 + checker_lint 2 + 호출 계약 27 + 수정 사이클 레인 3×2 = 90.

호출 계약 레인(라운드 1 P2 — 2026-08-12): TARGET 에 «BC 폴더»를 주면 검사기가
«표준 미채택 clean(exit 0)»으로 조용히 통과하던 사각을 고정한다 — BC 모양
TARGET 은 사용 오류 exit 1 이어야 한다(child_settings 라운드에서 파이프라인이
정확히 이 호출로 V1 트리를 전부 green 처리했다).

사용: python3 workspace/tools/fixture_matrix.py [--emit <md 경로>]
exit 0 = 전수 일치 / exit 2 = 불일치 존재 / exit 1 = 재료 결손.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

ROOT: Path = Path(__file__).resolve().parents[2]
S: Path = ROOT / "dddjango" / "scripts"
F: Path = ROOT / "workspace" / "eval" / "fixtures"
TOOLS: Path = ROOT / "workspace" / "tools"

PLAIN_PAIRS: "list[tuple[str, str]]" = [
    ("check-context-isolation.py", "context_isolation"),
    ("check-usecase-dto-placement.py", "usecase_dto"),
    ("check-mechanism-ownership.py", "mechanism_ownership"),
    ("check-synthetic-infra-exc.py", "synthetic_infra_exc"),
    ("check-ninja-boundary-middleware.py", "ninja_boundary_middleware"),
    ("check-transient-overmapping.py", "transient_overmapping"),
    ("check-idempotency-scope-creep.py", "idempotency_scope_creep"),
    ("check-common-container.py", "common_container"),
    ("check-app-container.py", "app_container"),
    ("check-public-surface-annotation.py", "public_surface"),
    ("check-choices-literal-consumption.py", "choices_literal"),
    ("check-test-config.py", "test_config"),
    ("check-response-schema-bypass.py", "response_schema_bypass"),
    ("check-composition-root.py", "composition_root"),
    ("check-db-table.py", "db_table"),
    ("check-transaction-boundary.py", "transaction_boundary"),
    ("check-event-publish.py", "event_publish"),
    ("check-broker-contract.py", "broker_contract"),
    ("check-missable-entrance.py", "missable_entrance"),
    ("check-naming.py", "naming"),
    ("check-domain-model.py", "domain_model"),
    ("check-business-vocabulary.py", "business_vocabulary"),
    ("check-port-adapter-pairing.py", "port_adapter_pairing"),
]
AUTO_PAIRS: "list[tuple[str, str]]" = [
    ("check-error-centralization.py", "error_centralization"),
    ("check-api-error-controller-contract.py", "api_error_controller"),
    ("check-openapi-error-declaration.py", "openapi_error_declaration"),
]
# 라운드 1′ 수정 사이클 레인(2026-08-12) — 검사기 «행동 변화» 고정용 추가 쌍.
# PLAIN_PAIRS 와 분리한 이유: 그 목록은 registry 27종 로스터의 재료(bc_registry_run
# import·호출 계약 레인)라 같은 검사기의 중복 등재가 로스터 assert 를 깨뜨린다.
EXTRA_LANES: "list[tuple[str, str]]" = [
    ("check-test-config.py", "test_config_entrance"),
    ("check-event-publish.py", "event_publish_leaf"),
    ("check-db-table.py", "db_table_choices"),
    # S2 F-B(2026-08-14) — #210 도메인 예외 면제: good=실선언 예외 클래스 직접 catch(구판 red→신판 green) ·
    # bad_rules=예외 칸 세탁 2종(함수 import·__init__ 재수출)은 계속 red.
    ("check-usecase-dto-placement.py", "usecase_dto_domain_exception"),
]

# Z-3A false-positive regression lanes. These fixtures express deliberate
# non-adoption or a domain meaning that shares a suffix with boundary DTOs.
NEGATIVE_LANES: "list[tuple[str, str, str]]" = [
    ("check-broker-contract.py", "broker_contract", "no_adoption"),
    ("check-composition-root.py", "composition_root", "no_api"),
    ("check-usecase-dto-placement.py", "usecase_dto", "no_api"),
    ("check-naming.py", "naming", "domain_results"),
    # 결정 2(2026-09-04) — 내용 없는 골격 파일(skeleton_placeholder)은 내용 규칙(#219·#635)의 대상이 아니다.
    ("check-port-adapter-pairing.py", "port_adapter_pairing", "skeleton_placeholder"),
    ("check-usecase-dto-placement.py", "usecase_dto", "skeleton_placeholder"),
]

POSITIVE_LANES: "list[tuple[str, str, str]]" = [
    ("check-usecase-dto-placement.py", "usecase_dto", "registrar_only"),
]


# 로스터 단일 출처 대조(2026-08-12 P3′) — 쌍 목록이 checker_registry 와 어긋나면 재료 결손.
sys.path.insert(0, str(S))
from checker_registry import REGISTRY  # noqa: E402

_pairs_roster: "dict[str, bool]" = {"check-layer-skeleton.py": False}
_pairs_roster.update({s: False for s, _ in PLAIN_PAIRS})
_pairs_roster.update({s: True for s, _ in AUTO_PAIRS})
assert _pairs_roster == {name: auto for name, auto in REGISTRY}, (
    "fixture 쌍 목록이 checker_registry 로스터와 어긋난다"
)


def build_cases() -> "list[tuple[str, list[str], str, int]]":
    """(라벨, argv, fixture 상대경로, 기대 exit)"""
    cases: list[tuple[str, list[str], str, int]] = []
    sk = "check-layer-skeleton.py"
    for sub, want in (("good_bc", 0), ("bad_legacy_flat", 2), ("bad_missing", 2),
                      ("good_promoted", 0), ("bad_promoted", 2)):
        fx = F / "skeleton" / sub
        cases.append((f"skeleton/{sub}", [sys.executable, str(S / sk), str(fx)], f"skeleton/{sub}", want))
    for script, fixture in PLAIN_PAIRS:
        for sub, want in (("good", 0), ("bad_rules", 2)):
            fx = F / fixture / sub
            cases.append((f"{fixture}/{sub}", [sys.executable, str(S / script), str(fx)], f"{fixture}/{sub}", want))
    for script, fixture, sub in NEGATIVE_LANES:
        fx = F / fixture / sub
        cases.append(
            (f"{fixture}/{sub}", [sys.executable, str(S / script), str(fx)], f"{fixture}/{sub}", 0))
    for script, fixture, sub in POSITIVE_LANES:
        fx = F / fixture / sub
        cases.append((f"{fixture}/{sub}", [sys.executable, str(S / script), str(fx)], f"{fixture}/{sub}", 2))
    for script, fixture in AUTO_PAIRS:
        for sub, want in (("good", 0), ("bad_rules", 2)):
            fx = F / fixture / sub
            cases.append(
                (f"{fixture}/{sub} (auto)",
                 [sys.executable, str(S / script), str(fx), "--error-profile", "auto"],
                 f"{fixture}/{sub}", want)
            )
    for script, fixture in EXTRA_LANES:
        for sub, want in (("good", 0), ("bad_rules", 2)):
            fx = F / fixture / sub
            cases.append((f"{fixture}/{sub}", [sys.executable, str(S / script), str(fx)], f"{fixture}/{sub}", want))
    for sub, want in (("good", 0), ("bad_rules", 2)):
        fx = F / "checker_lint" / sub
        cases.append(
            (f"checker_lint/{sub}",
             [sys.executable, str(TOOLS / "checker_lint.py"), "--scripts-dir", str(fx)],
             f"checker_lint/{sub}", want)
        )
    # selector(scope) 모드 레인(2026-08-15 S3-r2′ 수정 사이클) — composition 의
    # «ROOT_API_CONSTRUCTORS 직접 상속 로컬 클래스 팩토리» 인식 행동 고정.
    # good=직접 생성 기준선(exit 0) · bad_rules=subclass 팩토리는 분석이 «진행»돼
    # #437 위반으로 열거된다(exit 2 — 구판은 exit 1 분석 불능이라 앵커 차분 격리가
    # 불가능했다) · bad_usage=비상속 로컬 클래스 팩토리는 여전히 분석 불능(exit 1 —
    # 닫힌 허용 목록이 열리지 않았음 실증).
    comp_selector_args = [
        "--error-profile", "dddjango-code-json", "--scope", "public-v1",
        "--api-module", "config/api.py", "--urlconf-module", "config/urls.py",
        "--registrar-module", "application/lesson/driving_layer/api/api_router.py",
    ]
    for sub, want in (("good", 0), ("bad_rules", 2), ("bad_usage", 1)):
        fx = F / "composition_selector" / sub
        cases.append(
            (f"composition_selector/{sub} (selector)",
             [sys.executable, str(S / "check-composition-root.py"), str(fx), *comp_selector_args],
             f"composition_selector/{sub}", want)
        )
    # 호출 계약 레인 — TARGET=BC 폴더(층 폴더 직계 보유)는 clean 이 아니라 사용 오류다.
    bc_dir = F / "skeleton" / "good_bc" / "application" / "orders"
    for script in [sk] + [s for s, _ in PLAIN_PAIRS]:
        cases.append((f"invocation/{script}", [sys.executable, str(S / script), str(bc_dir)], "skeleton/good_bc(orders)", 1))
    for script, _ in AUTO_PAIRS:
        cases.append(
            (f"invocation/{script} (auto)",
             [sys.executable, str(S / script), str(bc_dir), "--error-profile", "auto"],
             "skeleton/good_bc(orders)", 1)
        )
    return cases


def main(argv: "list[str]") -> int:
    emit: "Path | None" = None
    if argv[:1] == ["--emit"]:
        if len(argv) < 2:
            print("사용: fixture_matrix.py [--emit <md 경로>]", file=sys.stderr)
            return 1
        emit = Path(argv[1])
    cases = build_cases()
    for _, cmd, fx_rel, _w in cases:
        if not Path(cmd[1]).is_file():
            print(f"재료 결손: {cmd[1]} 없음", file=sys.stderr)
            return 1
        fx_path = cmd[3] if cmd[2] == "--scripts-dir" else cmd[2]
        if not Path(fx_path).is_dir():
            print(f"재료 결손: fixture {fx_rel} 없음", file=sys.stderr)
            return 1

    lines: list[str] = [
        "| 검사기 | fixture | 기대 | 실측 | 판정 |",
        "|---|---|---|---|---|",
    ]
    mismatch: int = 0
    for label, cmd, _fx, want in cases:
        # fixture 는 git 밖 «임시 사본»으로 실행한다(hermetic) — 저장소 안 원본을 직접 주면
        # 검사기의 git/touched 인식이 커밋 상태에 따라 결과를 바꾼다(2026-08-12 release 게이트
        # 실측: fixture 가 untracked 일 땐 «신규»로 발화했는데 커밋 직후 tracked-무변이 되자
        # touched 슬라이스가 0건 — 임시 사본은 비-git이라 «전 후보 검사» fail-closed 레인을 탄다).
        fx_i: int = 3 if cmd[2] == "--scripts-dir" else 2
        with tempfile.TemporaryDirectory() as td:
            tmp_fx: Path = Path(td) / "fixture"
            shutil.copytree(cmd[fx_i], tmp_fx)
            run_cmd: list[str] = list(cmd)
            run_cmd[fx_i] = str(tmp_fx)
            # 사용자 환경의 DJR_FINDINGS_JSON 을 상속하면 이 하네스가 사용자의 실제
            # 레코드 파일에 테스트 레코드를 append 한다(T2-1 적대 검증 레인 S 7번 —
            # checker_baseline_matrix 판형). exit 만 재는 도구이므로 sink 를 아예 끊는다.
            env: "dict[str, str]" = dict(os.environ)
            env.pop("DJR_FINDINGS_JSON", None)
            got: int = subprocess.run(run_cmd, cwd=str(ROOT), stdout=subprocess.DEVNULL,
                                      stderr=subprocess.DEVNULL, env=env).returncode
        ok: bool = got == want
        if not ok:
            mismatch += 1
        checker: str = Path(cmd[1]).name if "--scripts-dir" not in cmd else "checker_lint.py"
        lines.append(f"| `{checker}` | {label} | {want} | {got} | {'✓' if ok else '✗ 불일치'} |")
    summary: str = f"케이스 {len(cases)} · 일치 {len(cases) - mismatch} · 불일치 {mismatch}"
    table: str = "\n".join(lines)
    print(table)
    print(summary)
    if emit is not None:
        emit.write_text(
            "# 전수 fixture 실측표 — 검사기 × 위반 fixture × exit\n\n"
            f"생성: {date.today().isoformat()} · `workspace/tools/fixture_matrix.py` 실행 산출물"
            "(손으로 고치지 않는다 — 재실행으로 재생성).\n\n"
            "「백스톱 실측 0」(5차 리뷰)의 종결 기록 — 검사기마다 자기 위반 fixture 에서 exit 2.\n"
            "eval v5 FROZEN — 실측은 이 fixture 결정 레인만.\n\n"
            f"{table}\n\n{summary}\n",
            encoding="utf-8",
        )
        print(f"실측표 기록: {emit}")
    return 0 if mismatch == 0 else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
