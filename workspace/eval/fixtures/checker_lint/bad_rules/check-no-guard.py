from __future__ import annotations

import sys
from pathlib import Path

LAYER_DIRS = ("domain_layer",)


def _is_adopted(root: Path) -> bool:
    return any(root.glob(f"*/{n}") for n in LAYER_DIRS)


def main(argv: list) -> int:
    root = Path(argv[0]) if argv else Path.cwd()
    if not _is_adopted(root):
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
