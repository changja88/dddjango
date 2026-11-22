from __future__ import annotations

import sys
from pathlib import Path

try:
    import shared_rule
except ImportError:
    sys.exit(1)

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))


def main(argv: list) -> int:
    return 0 if shared_rule.clean() else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
