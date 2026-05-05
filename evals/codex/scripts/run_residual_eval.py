#!/usr/bin/env python3
import argparse
import subprocess
import sys
from pathlib import Path

from build_residual_cases import build_residual_cases


def run(command):
    print("$ " + " ".join(str(part) for part in command), flush=True)
    subprocess.run(command, check=True)


def run_residual_eval(args):
    case_ids = build_residual_cases(
        args.source_conformance,
        args.source_cases,
        args.residual_cases,
        variant=args.variant or None,
    )
    if not case_ids:
        print("residual cases: none; skipping residual evaluation")
        return 0

    print(f"residual cases ({len(case_ids)}): {', '.join(case_ids)}", flush=True)
    run(
        [
            sys.executable,
            "evals/codex/scripts/init_iteration.py",
            "--cases",
            args.residual_cases,
            "--output",
            args.iteration,
            "--variant-set",
            args.variant_set,
        ]
    )
    run(
        [
            sys.executable,
            "evals/codex/scripts/run_prompts.py",
            "--iteration",
            args.iteration,
            "--variant",
            "baseline",
            "--keep-going",
        ]
    )
    run(
        [
            sys.executable,
            "evals/codex/scripts/run_prompts.py",
            "--iteration",
            args.iteration,
            "--variant",
            args.with_variant,
            "--keep-going",
        ]
    )
    for script in [
        "evals/codex/scripts/auto_grade_outputs.py",
        "evals/codex/scripts/grade_conformance.py",
        "evals/codex/scripts/render_report.py",
        "evals/codex/scripts/check_release_gate.py",
    ]:
        run([sys.executable, script, args.iteration])
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Run only residual cases from a previous conformance report."
    )
    parser.add_argument("--source-conformance", required=True)
    parser.add_argument("--source-cases", required=True)
    parser.add_argument("--residual-cases", required=True)
    parser.add_argument("--iteration", required=True)
    parser.add_argument("--variant", default="")
    parser.add_argument("--variant-set", default="plugin-real")
    parser.add_argument("--with-variant", default="dddjango-plugin")
    args = parser.parse_args()
    return run_residual_eval(args)


if __name__ == "__main__":
    raise SystemExit(main())
