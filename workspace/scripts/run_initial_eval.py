#!/usr/bin/env python3
"""Run the initial dddjango eval flow across one or more buckets."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import eval_run_common as common
import eval_run_identity as run_identity


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
    parser.add_argument("--try-number", type=int, default=1)
    parser.add_argument("--scope", choices=run_identity.SCOPE_CHOICES, default="full")
    parser.add_argument("--topic", default="current-baseline")
    parser.add_argument("--lv-up-analysis", default="")
    parser.add_argument("--lv-up-plan", default="")
    parser.add_argument("--case", action="append", help="Case id to run. Repeatable.")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--reasoning", default=DEFAULT_REASONING)
    parser.add_argument("--evaluator-model")
    parser.add_argument("--evaluator-reasoning", default=DEFAULT_EVALUATOR_REASONING)
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    parser.add_argument("--case-jobs", type=int, default=1)
    parser.add_argument("--rerun", action="store_true")
    parser.add_argument("--skip-exec", action="store_true")
    parser.add_argument("--skip-oracle", action="store_true")
    parser.add_argument("--render-only", action="store_true")
    parser.add_argument("--keep-going", action="store_true")
    return parser.parse_args(argv)


def validate_run_id(run_id: str) -> str:
    run_identity.validate_production_run_id(run_id)
    return run_id


def run_id_for_bucket(args: argparse.Namespace, bucket: str, bucket_count: int) -> str:
    if args.run_id is not None:
        if bucket_count != 1:
            raise SystemExit("explicit --run-id can only be used with one bucket")
        run_id = validate_run_id(args.run_id)
        identity = run_identity.parse_run_id(run_id)
        if identity.bucket != bucket:
            raise SystemExit(
                f"explicit --run-id bucket mismatch: run id bucket={identity.bucket}, selected bucket={bucket}"
            )
        return run_id
    return run_identity.build_run_id(
        bucket=bucket,
        try_number=args.try_number,
        scope=args.scope,
        topic=args.topic,
    )


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


def append_selected_case_args(
    command: list[str],
    args: argparse.Namespace,
    cases: list[str] | None,
) -> None:
    append_case_args(command, args.case if cases is None else cases)


def runner_command(
    args: argparse.Namespace,
    bucket: str,
    run_id: str,
    cases: list[str] | None = None,
) -> list[str]:
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
        "--lv-up-analysis",
        args.lv_up_analysis,
        "--lv-up-plan",
        args.lv_up_plan,
    ]
    append_selected_case_args(command, args, cases)
    if args.rerun:
        command.append("--rerun")
    if args.skip_exec:
        command.append("--skip-exec")
    return command


def evaluator_command(
    args: argparse.Namespace,
    bucket: str,
    run_id: str,
    cases: list[str] | None = None,
) -> list[str]:
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
    append_selected_case_args(command, args, cases)
    if args.rerun:
        command.append("--rerun")
    return command


def validator_command(
    args: argparse.Namespace,
    bucket: str,
    run_id: str,
    cases: list[str] | None = None,
) -> list[str]:
    command = [
        sys.executable,
        str(SCRIPT_DIR / "validate_eval_run.py"),
        "--bucket",
        bucket,
        "--run-id",
        run_id,
    ]
    append_selected_case_args(command, args, cases)
    if args.skip_oracle:
        command.append("--skip-oracle")
    if args.skip_exec:
        command.append("--allow-skipped-exits")
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


def run_pipeline_commands(bucket: str, commands: list[list[str]], *, case_id: str | None = None) -> bool:
    label = f"{bucket}/{case_id}" if case_id else bucket
    for command in commands:
        returncode = run_command(command)
        if returncode != 0:
            print(f"FAIL: {label}: {Path(command[1]).name} exited {returncode}", file=sys.stderr)
            return False
    return True


def report_path(bucket: str, run_id: str) -> Path:
    return Path("workspace/develop/eval") / bucket / "runs" / run_id / "analysis/report.html"


def case_pipeline_commands(
    args: argparse.Namespace,
    bucket: str,
    run_id: str,
    case_id: str,
) -> list[list[str]]:
    commands: list[list[str]] = []
    case = [case_id]
    if not args.render_only:
        commands.append(runner_command(args, bucket, run_id, case))
    if not args.skip_oracle and not args.render_only:
        commands.append(evaluator_command(args, bucket, run_id, case))
    commands.append(validator_command(args, bucket, run_id, case))
    return commands


def run_case_pipeline(args: argparse.Namespace, bucket: str, run_id: str, case_id: str) -> bool:
    return run_pipeline_commands(
        bucket,
        case_pipeline_commands(args, bucket, run_id, case_id),
        case_id=case_id,
    )


def selected_case_ids(bucket: str, selected: list[str] | None) -> list[str]:
    return [path.stem for path in common.selected_case_paths(bucket, selected)]


def run_cases_parallel(
    args: argparse.Namespace,
    bucket: str,
    run_id: str,
    case_ids: list[str],
) -> bool:
    worker_count = min(args.case_jobs, len(case_ids))
    print(f"run {bucket}: {len(case_ids)} case(s) with {worker_count} parallel job(s)", flush=True)
    failed = False
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        future_to_case = {
            executor.submit(run_case_pipeline, args, bucket, run_id, case_id): case_id
            for case_id in case_ids
        }
        for future in as_completed(future_to_case):
            case_id = future_to_case[future]
            try:
                ok = future.result()
            except Exception as exc:  # pragma: no cover - defensive subprocess orchestration guard
                print(f"FAIL: {bucket}/{case_id}: unexpected error: {exc}", file=sys.stderr)
                ok = False
            if not ok:
                failed = True
    return not failed


def final_bucket_commands(args: argparse.Namespace, bucket: str, run_id: str) -> list[list[str]]:
    return [
        validator_command(args, bucket, run_id),
        renderer_command(bucket, run_id),
    ]


def run_bucket(args: argparse.Namespace, bucket: str, run_id: str) -> bool:
    if args.case_jobs > 1 and not args.render_only:
        case_ids = selected_case_ids(bucket, args.case)
        if len(case_ids) > 1:
            if not run_cases_parallel(args, bucket, run_id, case_ids):
                return False
            if not run_pipeline_commands(bucket, final_bucket_commands(args, bucket, run_id)):
                return False
            print(report_path(bucket, run_id))
            return True

    commands: list[list[str]] = []
    if not args.render_only:
        commands.append(runner_command(args, bucket, run_id))
    if not args.skip_oracle and not args.render_only:
        commands.append(evaluator_command(args, bucket, run_id))
    commands.append(validator_command(args, bucket, run_id))
    commands.append(renderer_command(bucket, run_id))

    if not run_pipeline_commands(bucket, commands):
        return False

    print(report_path(bucket, run_id))
    return True


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.case_jobs < 1:
        raise SystemExit("case-jobs must be positive")
    buckets = selected_buckets(args.bucket)

    failed = False
    for bucket in buckets:
        run_id = run_id_for_bucket(args, bucket, len(buckets))
        ok = run_bucket(args, bucket, run_id)
        if not ok:
            failed = True
            if not args.keep_going:
                break

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
