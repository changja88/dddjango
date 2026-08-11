#!/usr/bin/env python3
"""전수 fixture 실측표 — 검사기 × 위반 fixture × 기대/실측 exit (5번 계획 Phase 4-3).

「백스톱 실측 0」(5차 리뷰 최대 발견)의 종결 장치: 검사기마다 자기 위반
fixture 에서 exit 2 가 나는지를 전수로 실측하고 표로 남긴다. eval v4 는
FROZEN 이므로 실측은 이 fixture 결정 레인만 쓴다.

케이스: skeleton 3 + 기존 15종×2 + API-error 3종×2(--error-profile auto)
       + 신설 8종×2 + checker_lint 2 = 57.

사용: python3 workspace/tools/fixture_matrix.py [--emit <md 경로>]
exit 0 = 전수 일치 / exit 2 = 불일치 존재 / exit 1 = 재료 결손.
"""
from __future__ import annotations

import subprocess
import sys
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


def build_cases() -> "list[tuple[str, list[str], str, int]]":
    """(라벨, argv, fixture 상대경로, 기대 exit)"""
    cases: list[tuple[str, list[str], str, int]] = []
    sk = "check-layer-skeleton.py"
    for sub, want in (("good_bc", 0), ("bad_legacy_flat", 2), ("bad_missing", 2)):
        fx = F / "skeleton" / sub
        cases.append((f"skeleton/{sub}", [sys.executable, str(S / sk), str(fx)], f"skeleton/{sub}", want))
    for script, fixture in PLAIN_PAIRS:
        for sub, want in (("good", 0), ("bad_rules", 2)):
            fx = F / fixture / sub
            cases.append((f"{fixture}/{sub}", [sys.executable, str(S / script), str(fx)], f"{fixture}/{sub}", want))
    for script, fixture in AUTO_PAIRS:
        for sub, want in (("good", 0), ("bad_rules", 2)):
            fx = F / fixture / sub
            cases.append(
                (f"{fixture}/{sub} (auto)",
                 [sys.executable, str(S / script), str(fx), "--error-profile", "auto"],
                 f"{fixture}/{sub}", want)
            )
    for sub, want in (("good", 0), ("bad_rules", 2)):
        fx = F / "checker_lint" / sub
        cases.append(
            (f"checker_lint/{sub}",
             [sys.executable, str(TOOLS / "checker_lint.py"), "--scripts-dir", str(fx)],
             f"checker_lint/{sub}", want)
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
        got: int = subprocess.run(cmd, cwd=str(ROOT), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
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
            "eval v4 FROZEN — 실측은 이 fixture 결정 레인만.\n\n"
            f"{table}\n\n{summary}\n",
            encoding="utf-8",
        )
        print(f"실측표 기록: {emit}")
    return 0 if mismatch == 0 else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
