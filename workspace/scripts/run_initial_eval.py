#!/usr/bin/env python3
"""Run the initial dddjango eval flow across one or more buckets."""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import eval_run_common as common


REPO_ROOT = common.REPO_ROOT
DEFAULT_MODEL = "gpt-5.5"
DEFAULT_REASONING = "xhigh"
DEFAULT_EVALUATOR_REASONING = "high"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--bucket",
        action="append",
        choices=(*common.BUCKETS, "all"),
        help="Eval bucket to run. Repeatable. Defaults to all buckets.",
    )
    parser.add_argument("--run-id")
    parser.add_argument("--case", action="append", help="Case id to run. Repeatable.")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--reasoning", default=DEFAULT_REASONING)
    parser.add_argument("--evaluator-model")
    parser.add_argument("--evaluator-reasoning", default=DEFAULT_EVALUATOR_REASONING)
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    parser.add_argument("--rerun", action="store_true")
    parser.add_argument("--skip-exec", action="store_true")
    parser.add_argument("--skip-oracle", action="store_true")
    parser.add_argument("--render-only", action="store_true")
    parser.add_argument("--keep-going", action="store_true")
    return parser.parse_args(argv)


def now_text() -> str:
    return datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y%m%d-%H%M")


def validate_run_id(run_id: str) -> str:
    path = Path(run_id)
    if (
        not run_id
        or path.is_absolute()
        or len(path.parts) != 1
        or run_id in {".", ".."}
        or ".." in run_id
        or "/" in run_id
        or "\\" in run_id
    ):
        raise SystemExit(f"unsafe run id: {run_id}")
    return run_id


def selected_buckets(raw_buckets: list[str] | None) -> list[str]:
    if not raw_buckets or "all" in raw_buckets:
        return list(common.BUCKETS)

    buckets: list[str] = []
    for bucket in raw_buckets:
        if bucket not in buckets:
            buckets.append(bucket)
    return buckets


def append_case_args(command: list[str], cases: list[str] | None) -> None:
    for case_id in cases or []:
        command.extend(["--case", case_id])


def runner_command(args: argparse.Namespace, bucket: str, run_id: str) -> list[str]:
    command = [
        sys.executable,
        str(SCRIPT_DIR / "run_eval_bucket.py"),
        "--bucket",
        bucket,
        "--run-id",
        run_id,
        "--model",
        args.model,
        "--reasoning",
        args.reasoning,
        "--timeout-seconds",
        str(args.timeout_seconds),
    ]
    append_case_args(command, args.case)
    if args.rerun:
        command.append("--rerun")
    if args.skip_exec:
        command.append("--skip-exec")
    return command


def evaluator_command(args: argparse.Namespace, bucket: str, run_id: str) -> list[str]:
    command = [
        sys.executable,
        str(SCRIPT_DIR / "evaluate_eval_run.py"),
        "--bucket",
        bucket,
        "--run-id",
        run_id,
        "--model",
        args.evaluator_model or args.model,
        "--reasoning",
        args.evaluator_reasoning,
        "--timeout-seconds",
        str(args.timeout_seconds),
    ]
    append_case_args(command, args.case)
    if args.rerun:
        command.append("--rerun")
    return command


def validator_command(args: argparse.Namespace, bucket: str, run_id: str) -> list[str]:
    command = [
        sys.executable,
        str(SCRIPT_DIR / "validate_eval_run.py"),
        "--bucket",
        bucket,
        "--run-id",
        run_id,
    ]
    append_case_args(command, args.case)
    if args.skip_oracle or args.render_only:
        command.append("--skip-oracle")
    return command


def renderer_command(bucket: str, run_id: str) -> list[str]:
    return [
        sys.executable,
        str(SCRIPT_DIR / "render_eval_review_html.py"),
        "--bucket",
        bucket,
        "--run-id",
        run_id,
    ]


def run_command(command: list[str]) -> int:
    result = subprocess.run(command, cwd=REPO_ROOT, check=False)
    return result.returncode


def report_path(bucket: str, run_id: str) -> Path:
    return Path("workspace/develop/eval") / bucket / "runs" / run_id / "analysis/report.html"


def run_bucket(args: argparse.Namespace, bucket: str, run_id: str) -> bool:
    commands: list[list[str]] = []
    if not args.render_only:
        commands.append(runner_command(args, bucket, run_id))
    if not args.skip_oracle and not args.render_only:
        commands.append(evaluator_command(args, bucket, run_id))
    commands.append(validator_command(args, bucket, run_id))
    commands.append(renderer_command(bucket, run_id))

    for command in commands:
        returncode = run_command(command)
        if returncode != 0:
            print(f"FAIL: {bucket}: {Path(command[1]).name} exited {returncode}", file=sys.stderr)
            return False

    print(report_path(bucket, run_id))
    return True


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    run_id = validate_run_id(args.run_id if args.run_id is not None else f"{now_text()}-initial-eval")
    buckets = selected_buckets(args.bucket)

    failed = False
    for bucket in buckets:
        ok = run_bucket(args, bucket, run_id)
        if not ok:
            failed = True
            if not args.keep_going:
                break

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
