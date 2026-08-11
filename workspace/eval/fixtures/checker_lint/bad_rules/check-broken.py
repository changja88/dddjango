from __future__ import annotations

import sys
from pathlib import Path

LAYER_DIRS = ("domain_layer", "application_layer")
ALLOW_PATHS = ("myproject/special/helper.py",)


def _has_adoption_signal(bc_dir: Path) -> bool:
    return any((bc_dir / n).is_dir() for n in LAYER_DIRS)


def main(argv: list) -> int:
    root = Path(argv[0]) if argv else Path.cwd()
    if not (root / ".git").is_dir():
        return 0
    baseline = open(root / "violations_baseline.txt").read()
    bcs = [p for p in (root / "application").glob("*") if p.is_dir()]
    targets = _touched_filter([p for b in bcs if _has_adoption_signal(b) for p in b.rglob("*.py")])
    adopted = [b for b in bcs if _has_adoption_signal(b)]
    if adopted and not targets:
        print("blocker: 대상 0건 (#74)")
        return 2
    return 0


def _touched_filter(targets: list) -> list:
    return targets


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
