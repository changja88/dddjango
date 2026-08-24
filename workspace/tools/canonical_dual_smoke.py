#!/usr/bin/env python3
"""#417 부칙(2026-08-25) «정본 이중화 금지» 채널의 회귀 pin — error 계열 3종 전수.

두 정본 변형(framework/ninja/framework_error_schema.py · framework/django_ninja/error_schema.py)
이 동시에 실재하는 임시 트리에서, `_select_canonical` 이 검사기 3종 각각에서
사용 오류 exit 1 + «정본 공용 오류 스키마 이중 실재» stderr 문면을 내는지 단언한다.
(fixture 레인은 exit {2} 판형이라 exit-1 채널을 pin 할 수 없어 이 스모크가 소유한다 —
대조 리뷰 2026-08-25 major 처분.)
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT: Path = Path(__file__).resolve().parents[2]
SCRIPTS: Path = REPO_ROOT / "dddjango" / "scripts"
# (스크립트, 추가 argv) — api 검사기는 --error-profile 이 파스 필수라 auto 를 붙여
# _select_canonical 도달을 보장한다(auto 라도 정본 확정은 파스 직후 실행된다).
CHECKERS: "tuple[tuple[str, tuple[str, ...]], ...]" = (
    ("check-error-centralization.py", ()),
    ("check-api-error-controller-contract.py", ("--error-profile", "auto")),
    ("check-openapi-error-declaration.py", ()),
)
SENTENCE: str = "정본 공용 오류 스키마 이중 실재"


def build_dual_repo(root: Path) -> None:
    for d, b in (("framework/ninja", "framework_error_schema"),
                 ("framework/django_ninja", "error_schema")):
        (root / d).mkdir(parents=True)
        (root / d / "__init__.py").write_text("", encoding="utf-8")
        (root / d / f"{b}.py").write_text(
            "from ninja import Schema\n\n\nclass FrameworkErrorSchema(Schema):\n    code: str\n",
            encoding="utf-8")


def main() -> int:
    bad = 0
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "repo"
        build_dual_repo(repo)
        for script, extra in CHECKERS:
            proc = subprocess.run(
                [sys.executable, str(SCRIPTS / script), str(repo), *extra],
                capture_output=True, text=True,
            )
            ok = proc.returncode == 1 and SENTENCE in proc.stderr
            mark = "✓" if ok else "✗"
            print(f"{mark} dual-canonical {script}: exit {proc.returncode}"
                  f" · 문면 {'유' if SENTENCE in proc.stderr else '무'}")
            if not ok:
                bad += 1
    print(f"[canonical-dual-smoke] 검사기 {len(CHECKERS)} · 실패 {bad}")
    return 2 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
