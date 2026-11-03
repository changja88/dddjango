#!/usr/bin/env python3
"""test_watch.py 픽스처 러너(core) — dddjango-web 의 도구 시험 `fixtures_test_watch.py` 를 core 사본
`dddjango/scripts/test_watch.py`(+ `watch_probe/`)에 대어 돈다. 시험 글은 한 벌(web 쪽)이고, 두 사본이 byte 같음은
Makefile `verify-base-core` 의 cmp 줄이 따로 본다. pytest 장난감은 저장소 뿌리 `.venv-probe` 로 돈다(없으면 FAIL — make probe-env).
exit = 픽스처 exit(0 = 전건 통과 · 1 = 실패 있음).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT: Path = Path(__file__).resolve().parents[2]
FIXTURE: Path = ROOT / "dddjango-web" / "scripts" / "test" / "fixtures_test_watch.py"
TOOL: Path = ROOT / "dddjango" / "scripts" / "test_watch.py"


def main() -> int:
    return subprocess.run([sys.executable, str(FIXTURE), "--tool", str(TOOL), *sys.argv[1:]]).returncode


if __name__ == "__main__":
    sys.exit(main())
