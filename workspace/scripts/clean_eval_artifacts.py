#!/usr/bin/env python3
"""Clean generated eval run artifacts."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
EVAL_ROOT = REPO_ROOT / "workspace/develop/eval"
BUCKETS = ("response", "code", "plugin", "runtime", "source", "workflow")
CONFIRM_FLAG = "--confirm-delete-generated-eval-artifacts"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        CONFIRM_FLAG,
        dest="confirmed",
        action="store_true",
        help="Delete generated eval artifacts. Without this flag the script only prints targets.",
    )
    return parser.parse_args(argv)


def children(path: Path) -> list[Path]:
    if not path.is_dir():
        return []
    return sorted(path.iterdir())


def collect_delete_targets() -> list[Path]:
    targets: list[Path] = []
    for bucket in BUCKETS:
        targets.extend(children(EVAL_ROOT / bucket / "runs"))
        targets.extend(children(EVAL_ROOT / bucket / "latest"))
        targets.extend(children(EVAL_ROOT / bucket / "latest-valid"))
    return sorted(targets)


def remove_target(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    targets = collect_delete_targets()
    mode = "DELETE" if args.confirmed else "DRY-RUN"
    print(f"{mode}: {len(targets)} generated eval artifact path(s)")
    for path in targets:
        print(path.relative_to(REPO_ROOT).as_posix())
    if args.confirmed:
        for path in targets:
            remove_target(path)
    else:
        print(f"Re-run with {CONFIRM_FLAG} to delete these paths.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
