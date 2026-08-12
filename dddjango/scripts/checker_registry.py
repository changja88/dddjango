#!/usr/bin/env python3
"""registry 27종의 «단일 출처» — 게이트·판정 도구·fixture 하네스가 같은 로스터를 소비한다.

순서는 `commands/dddjango.md` 의 «정확한 checker registry와 소유권(순서 고정)» 절과
같다(1~27). AUTO 플래그는 positional 기본 호출에 `--error-profile auto` 를 붙이는
API-error 3종이다(#2·#15·#5 — error-response scope 별 정식 selector 렌더는
commands 절차 소유이고, 이 로스터의 auto 는 «프로필 무관 선행 슬라이스» 실행용이다).

자기 검증(2026-08-12 라운드 1′ P3′): 이 목록과 같은 폴더의 `check-*.py` 실재 집합이
어긋나면 import 시점에 AssertionError — 산문 목록↔파일 드리프트를 기계가 막는다.
"""
from __future__ import annotations

from pathlib import Path

SCRIPTS_DIR: Path = Path(__file__).resolve().parent

# (스크립트 이름, auto 프로필 플래그) — 순서 고정(commands registry 1~27).
REGISTRY: "tuple[tuple[str, bool], ...]" = (
    ("check-mechanism-ownership.py", False),
    ("check-error-centralization.py", True),
    ("check-response-schema-bypass.py", False),
    ("check-layer-skeleton.py", False),
    ("check-openapi-error-declaration.py", True),
    ("check-context-isolation.py", False),
    ("check-app-container.py", False),
    ("check-ninja-boundary-middleware.py", False),
    ("check-common-container.py", False),
    ("check-idempotency-scope-creep.py", False),
    ("check-public-surface-annotation.py", False),
    ("check-test-config.py", False),
    ("check-transient-overmapping.py", False),
    ("check-synthetic-infra-exc.py", False),
    ("check-api-error-controller-contract.py", True),
    ("check-composition-root.py", False),
    ("check-db-table.py", False),
    ("check-choices-literal-consumption.py", False),
    ("check-usecase-dto-placement.py", False),
    ("check-transaction-boundary.py", False),
    ("check-domain-model.py", False),
    ("check-port-adapter-pairing.py", False),
    ("check-event-publish.py", False),
    ("check-broker-contract.py", False),
    ("check-missable-entrance.py", False),
    ("check-naming.py", False),
    ("check-business-vocabulary.py", False),
)

_listed: "set[str]" = {name for name, _ in REGISTRY}
_found: "set[str]" = {p.name for p in SCRIPTS_DIR.glob("check-*.py")}
assert _listed == _found, (
    f"registry 목록↔파일 드리프트 — 목록에만 {sorted(_listed - _found)} · "
    f"파일에만 {sorted(_found - _listed)}"
)
assert len(REGISTRY) == 27, f"registry 는 27종이어야 한다 — 지금 {len(REGISTRY)}"


def checker_argv(python: str, script: str, target: str, auto: bool) -> "list[str]":
    """로스터 한 항목의 positional 기본 호출 argv 를 만든다."""
    argv: "list[str]" = [python, str(SCRIPTS_DIR / script), target]
    if auto:
        argv += ["--error-profile", "auto"]
    return argv
