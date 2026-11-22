from __future__ import annotations

import sys
from pathlib import Path

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared_rule import DJANGO_APP_MARKERS

NEW_LAYERS = {"driving_layer", "application_layer", "domain_layer", "driven_layer"}


def _has_adoption_signal(bc_dir: Path) -> bool:
    return any((bc_dir / n).is_dir() for n in NEW_LAYERS) or any(
        (bc_dir / m).is_file() for m in DJANGO_APP_MARKERS)


def main(argv: list) -> int:
    root = Path(argv[0]) if argv else Path.cwd()
    bcs = [p for p in (root / "application").glob("*") if p.is_dir()]
    adopted = [b for b in bcs if _has_adoption_signal(b)]
    targets = [p for b in adopted for p in b.rglob("*.py")]
    if adopted and not targets:
        print("blocker: 채택 신호는 있는데 대상이 0건이다 — 조용한 무동작을 금지한다(#74)")
        return 2
    touched = _touched_filter(targets)
    return 0 if touched is not None else 0


def _touched_filter(targets: list) -> list:
    return targets


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
