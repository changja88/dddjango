#!/usr/bin/env python3
"""bc_registry_run 의 로스터 계약 스모크 — 단일-BC 그림자의 #365 과탐/진양성 고정.

배경(2026-08-13 · 라운드 2 실증): 그림자 사본에 대상 BC 만 담기면 `bc_names` 가
{대상} 하나로 줄어, 정당한 이웃 BC 대상 ACL(`anticorruption_layer/<이웃>/`)이
#365(«우리 다른 BC 전용») 과탐으로 발화했다. 수정은 검사기(파일트리 기반·무결)가
아니라 하네스 — `check-port-adapter-pairing.py` 를 ROSTER_AWARE(이웃 빈 스텁 둘째 판)에
편입한다. 이 스모크는 그 계약 두 면을 고정한다:

  A) 이웃 BC 대상 ACL 은 #365 를 내지 않는다 (과탐 소멸 — 수정 전 red 실증됨)
  B) 로스터 밖 이름 대상 ACL 은 여전히 #365 를 낸다 (진양성 보존 — fixture
     bad_rules 의 `payment_vendor/` 레인과 동형. exit-단위 매트릭스가 못 보는
     레인 사멸을 규칙-단위로 감시)

사용: python3 bc_registry_smoke.py  → exit 0 = 두 단언 충족 / exit 2 = 위반.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS: Path = Path(__file__).resolve().parent
RUNNER: Path = TOOLS / "bc_registry_run.py"



def _scrubbed_env() -> "dict[str, str]":
    """검사기 하위 실행 env — 사용자 DJR_FINDINGS_JSON 오염 차단(T2-1 적대 검증 레인 S 7번 잔여)."""
    env = dict(os.environ)
    env.pop("DJR_FINDINGS_JSON", None)
    return env

def _mk(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)
    (p / "__init__.py").write_text("", encoding="utf-8")


def build_mini_repo(root: Path) -> None:
    """2-BC 최소 재료: alpha 의 ACL 이 이웃 beta(정당)와 vendorx(로스터 밖)를 가진다."""
    (root / "application").mkdir(parents=True)
    (root / "application" / "__init__.py").write_text("", encoding="utf-8")
    _mk(root / "application" / "beta")
    acl: Path = root / "application" / "alpha" / "driven_layer" / "adapter" / "anticorruption_layer"
    _mk(root / "application" / "alpha")
    _mk(root / "application" / "alpha" / "driven_layer")
    _mk(root / "application" / "alpha" / "driven_layer" / "adapter")
    _mk(acl)
    _mk(acl / "beta")
    _mk(acl / "vendorx")
    # #365 부칙(2026-08-25) — 통신 축 import 를 가진 위장 ACL 은 blocker 를 유지해야 한다.
    _mk(acl / "vendory")
    (acl / "vendory" / "quote_adapter.py").write_text(
        "import urllib.request\n", encoding="utf-8")


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        repo: Path = Path(td) / "repo"
        build_mini_repo(repo)
        proc = subprocess.run(
            [sys.executable, str(RUNNER), str(repo), "alpha"],
            env=_scrubbed_env(),
            capture_output=True, text=True,
        )
        out: str = proc.stdout + proc.stderr
    beta_hits: int = sum(1 for ln in out.splitlines() if "[#365]" in ln and "anticorruption_layer/beta" in ln)
    # #365 부칙(2026-08-25): 순수 스텁(vendorx)은 후보(ⓓ) 발화 = 비침묵 · 통신 위장(vendory)은 blocker 유지.
    vendor_cand: int = sum(1 for ln in out.splitlines() if "ⓓ#365" in ln and "anticorruption_layer/vendorx" in ln)
    vendor_block: int = sum(1 for ln in out.splitlines() if "[#365]" in ln and "anticorruption_layer/vendory" in ln)
    bad: int = 0
    if beta_hits:
        print(f"✗ A 위반: 이웃 BC(beta) 대상 ACL 에 #365 과탐 {beta_hits}건 — 로스터 공급(ROSTER_AWARE) 부재")
        bad += 1
    else:
        print("✓ A: 이웃 BC 대상 ACL 과탐 0")
    if not vendor_cand:
        print("✗ B 위반: 로스터 밖 순수 스텁(vendorx)의 ⓓ#365 후보가 침묵 — 비침묵 창구 사멸")
        bad += 1
    else:
        print(f"✓ B: 로스터 밖 순수 스텁 후보 발화 유지 ({vendor_cand}건)")
    if not vendor_block:
        print("✗ C 위반: 통신 위장(vendory) ACL 의 #365 blocker 가 침묵 — 규칙 레인 사멸")
        bad += 1
    else:
        print(f"✓ C: 통신 위장 ACL blocker 유지 ({vendor_block}건)")
    return 2 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
