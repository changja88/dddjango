#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evals.codex.scripts.init_iteration import create_iteration


def main():
    parser = argparse.ArgumentParser(
        description="Create a manual Claude plugin evaluation iteration workspace."
    )
    parser.add_argument(
        "--cases",
        default="evals/codex/cases/pilot.jsonl",
        help="Path to evaluation cases JSONL.",
    )
    parser.add_argument(
        "--schema",
        default="evals/codex/rubrics/grading-schema.json",
        help="Path to grading schema JSON.",
    )
    parser.add_argument(
        "--output",
        default="workspace/claude-eval/iteration-1",
        help="Directory to create for this evaluation iteration.",
    )
    args = parser.parse_args()

    output = create_iteration(args.cases, args.schema, args.output)
    summary = Path(output) / "SUMMARY.md"
    summary.write_text(
        summary.read_text().replace(
            "# Codex dddjango Evaluation Iteration",
            "# Claude dddjango Evaluation Iteration",
        )
    )
    print(f"created evaluation iteration: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
