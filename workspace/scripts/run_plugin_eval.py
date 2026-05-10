#!/usr/bin/env python3
"""Run dddjango plugin eval public packets with and without the plugin config."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


REPO_ROOT = Path("/Users/hyun/Desktop/dddjango")
PUBLIC_CASES = REPO_ROOT / "workspace/develop/evals/cases/plugin/public"
RUNS_DIR = REPO_ROOT / "workspace/develop/evals/runs"
DEFAULT_MODEL = "gpt-5.5"
DEFAULT_REASONING = "xhigh"


@dataclass(frozen=True)
class Variant:
    name: str
    ignore_user_config: bool


VARIANTS = {
    "baseline": Variant("baseline", True),
    "with-dddjango": Variant("with-dddjango", False),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", help="Existing or new run id. Defaults to timestamped id.")
    parser.add_argument("--case", action="append", help="Case id to run, e.g. case-001. Repeatable.")
    parser.add_argument(
        "--variant",
        action="append",
        choices=sorted(VARIANTS),
        help="Variant to run. Defaults to both variants.",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--reasoning", default=DEFAULT_REASONING)
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    parser.add_argument("--rerun", action="store_true", help="Overwrite existing non-empty outputs.")
    parser.add_argument("--skip-exec", action="store_true", help="Create metadata/prompt artifacts only.")
    return parser.parse_args()


def now_text() -> str:
    return datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y%m%d-%H%M")


def case_paths(selected: list[str] | None) -> list[Path]:
    paths = sorted(PUBLIC_CASES.glob("case-*.md"))
    if not selected:
        return paths
    wanted = set(selected)
    found = {path.stem for path in paths}
    missing = sorted(wanted - found)
    if missing:
        raise SystemExit(f"Unknown case id(s): {', '.join(missing)}")
    return [path for path in paths if path.stem in wanted]


def build_prompt(public_packet: str) -> str:
    return (
        "You are executing a public forward-eval packet for the dddjango plugin.\n"
        "Use only the public packet below and task-local repository files if needed.\n"
        "Do not read workspace/develop/rubrics, workspace/develop/evals/cases/plugin/private, "
        "prior run reports, or prior findings.\n"
        "Do not modify files. If a check is not actually run, state that it was not run.\n"
        "Keep the answer concise but include commands actually run and checks not run.\n\n"
        "----- PUBLIC PACKET START -----\n"
        f"{public_packet.rstrip()}\n"
        "----- PUBLIC PACKET END -----\n"
    )


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_command(
    command: list[str],
    *,
    prompt: str | None,
    cwd: Path,
    timeout_seconds: int,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.setdefault("NO_COLOR", "1")
    return subprocess.run(
        command,
        cwd=cwd,
        input=prompt,
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
        env=env,
        check=False,
    )


def codex_exec_command(
    variant: Variant,
    *,
    output_path: Path,
    model: str,
    reasoning: str,
) -> list[str]:
    command = [
        "codex",
        "-a",
        "never",
        "exec",
        "--ephemeral",
        "--color",
        "never",
        "-C",
        str(REPO_ROOT),
        "-s",
        "read-only",
        "-m",
        model,
        "-c",
        f'model_reasoning_effort="{reasoning}"',
        "-o",
        str(output_path),
    ]
    if variant.ignore_user_config:
        command.append("--ignore-user-config")
    command.append("-")
    return command


def main() -> int:
    args = parse_args()
    run_id = args.run_id or f"{now_text()}-plugin-eval"
    run_dir = RUNS_DIR / run_id
    raw_dir = run_dir / "raw"
    analysis_dir = run_dir / "analysis"
    raw_dir.mkdir(parents=True, exist_ok=True)
    analysis_dir.mkdir(parents=True, exist_ok=True)

    cases = case_paths(args.case)
    variants = [VARIANTS[name] for name in (args.variant or ["baseline", "with-dddjango"])]

    write_text(run_dir / "RUN_ID.txt", run_id + "\n")
    write_text(
        run_dir / "operator-notes.md",
        "\n".join(
            [
                f"# Eval Run {run_id}",
                "",
                f"- Started: {datetime.now(ZoneInfo('Asia/Seoul')).isoformat(timespec='seconds')}",
                f"- Model: {args.model}",
                f"- Reasoning: {args.reasoning}",
                "- Baseline command uses `codex exec --ignore-user-config`.",
                "- With-dddjango command uses the active user config and enabled dddjango plugin.",
                "- Sandbox: read-only.",
                "- Approval policy: never.",
                "",
            ]
        ),
    )

    for case_path in cases:
        case_id = case_path.stem
        public_packet = case_path.read_text(encoding="utf-8")
        prompt = build_prompt(public_packet)
        shutil.copyfile(case_path, raw_dir / f"{case_id}-public-prompt.md")
        write_text(raw_dir / f"{case_id}-operator-prompt.txt", prompt)

        prompt_input_path = raw_dir / f"{case_id}-prompt-input.json"
        if args.rerun or not prompt_input_path.exists():
            debug_result = run_command(
                ["codex", "debug", "prompt-input", prompt],
                prompt=None,
                cwd=REPO_ROOT,
                timeout_seconds=args.timeout_seconds,
            )
            write_text(prompt_input_path, debug_result.stdout)
            write_text(raw_dir / f"{case_id}-prompt-input.stderr.txt", debug_result.stderr)

        for variant in variants:
            output_path = raw_dir / f"{case_id}-{variant.name}.txt"
            stdout_path = raw_dir / f"{case_id}-{variant.name}-events.jsonl"
            stderr_path = raw_dir / f"{case_id}-{variant.name}.stderr.txt"
            command_path = raw_dir / f"{case_id}-{variant.name}-command.txt"
            exit_path = raw_dir / f"{case_id}-{variant.name}-exit.txt"
            if output_path.exists() and output_path.stat().st_size > 0 and not args.rerun:
                print(f"skip existing {case_id} {variant.name}")
                continue
            command = codex_exec_command(
                variant,
                output_path=output_path,
                model=args.model,
                reasoning=args.reasoning,
            )
            write_text(command_path, " ".join(command) + "\n")
            if args.skip_exec:
                write_text(output_path, "NOT RUN: --skip-exec was used.\n")
                write_text(exit_path, "skipped\n")
                continue
            print(f"run {case_id} {variant.name}", flush=True)
            try:
                result = run_command(
                    command,
                    prompt=prompt,
                    cwd=REPO_ROOT,
                    timeout_seconds=args.timeout_seconds,
                )
            except subprocess.TimeoutExpired as exc:
                write_text(stdout_path, exc.stdout or "")
                write_text(stderr_path, exc.stderr or "")
                write_text(exit_path, f"timeout after {args.timeout_seconds}s\n")
                continue
            write_text(stdout_path, result.stdout)
            write_text(stderr_path, result.stderr)
            write_text(exit_path, str(result.returncode) + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
