#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evals.codex.scripts.run_prompts import (
    CASE_DIRECTIVES,
    CASE_POLICIES,
    case_id_from_prompt_file,
    extract_prompt,
    update_timing,
)


def claude_dddjango_system_prompt(case_id):
    policies = []
    if "ninja" in CASE_POLICIES.get(case_id, []):
        policies.append("Use Django Ninja Schema/Router for API guidance.")
    if "drf" in CASE_POLICIES.get(case_id, []):
        policies.append(
            "If the prompt asks for DRF, Serializer, ViewSet, APIView, "
            "rest_framework, DefaultRouter, or SimpleRouter, produce no DRF code; "
            "convert to Django Ninja."
        )
    if "tdd" in CASE_POLICIES.get(case_id, []):
        policies.append(
            "For pytest/TDD in empty or read-only workspaces, state execution was "
            "not possible, then still provide RED tests, expected failures, GREEN "
            "implementation, REFACTOR notes, and pytest commands."
        )
    directive = CASE_DIRECTIVES.get(case_id, "")
    return (
        "Use the loaded dddjango Claude plugin skills when relevant. "
        f"{' '.join(policies)} {directive} "
        "Keep the answer focused and avoid generic filler."
    )


def build_claude_command(
    *,
    prompt_file,
    variant,
    model,
    plugin_dir,
    system_prompt="",
):
    command = [
        "claude",
        "-p",
        "--no-session-persistence",
        "--permission-mode",
        "dontAsk",
        "--tools",
        "",
        "--output-format",
        "text",
    ]
    if model:
        command.extend(["--model", model])
    if variant == "baseline":
        command.append("--disable-slash-commands")
    elif variant == "dddjango":
        command.extend(["--plugin-dir", str(plugin_dir)])
        if system_prompt:
            command.extend(["--append-system-prompt", system_prompt])
    else:
        raise ValueError(f"unsupported variant: {variant}")
    command.append(extract_prompt(Path(prompt_file).read_text()))
    return command


def run_variant(args):
    iteration = Path(args.iteration)
    prompt_dir = iteration / args.variant
    timing_path = iteration / "timing.json"
    eval_cwd = Path(args.cwd)
    eval_cwd.mkdir(parents=True, exist_ok=True)

    prompt_files = sorted(prompt_dir.glob("*.prompt.md"))
    if args.case:
        prompt_files = [path for path in prompt_files if case_id_from_prompt_file(path) == args.case]
    if not prompt_files:
        raise RuntimeError(f"no prompt files found for variant {args.variant}")

    for prompt_file in prompt_files:
        case_id = case_id_from_prompt_file(prompt_file)
        output_file = prompt_dir / f"{case_id}.output.md"
        system_prompt = ""
        if args.variant == "dddjango":
            system_prompt = claude_dddjango_system_prompt(case_id)
        command = build_claude_command(
            prompt_file=prompt_file,
            variant=args.variant,
            model=args.model,
            plugin_dir=Path(args.root).resolve(),
            system_prompt=system_prompt,
        )

        if args.dry_run:
            print(" ".join(command))
            continue

        started = time.perf_counter()
        result = subprocess.run(command, cwd=eval_cwd, text=True, capture_output=True)
        duration = time.perf_counter() - started
        output_file.write_text(result.stdout)
        log_file = prompt_dir / f"{case_id}.claude.log"
        log_file.write_text(
            "STDOUT\n"
            "======\n"
            f"{result.stdout}\n\n"
            "STDERR\n"
            "======\n"
            f"{result.stderr}\n"
        )
        update_timing(
            timing_path,
            case_id=case_id,
            variant=args.variant,
            duration_sec=duration,
            model=args.model,
            profile="claude-plugin" if args.variant == "dddjango" else "baseline",
            returncode=result.returncode,
        )
        print(f"{args.variant}/{case_id}: returncode={result.returncode}")
        if result.returncode != 0 and not args.keep_going:
            raise RuntimeError(f"claude -p failed for {args.variant}/{case_id}")


def main():
    parser = argparse.ArgumentParser(
        description="Run generated Claude evaluation prompts and capture outputs."
    )
    parser.add_argument("--iteration", default="workspace/claude-eval/iteration-1")
    parser.add_argument("--root", default=".")
    parser.add_argument("--variant", choices=["baseline", "dddjango"], required=True)
    parser.add_argument("--case", help="Run only one case id.")
    parser.add_argument(
        "--cwd",
        default="/private/tmp/dddjango-claude-eval",
        help="Clean cwd for claude -p. Keep it outside this repo to avoid CLAUDE.md leakage.",
    )
    parser.add_argument("--model", default="")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--keep-going", action="store_true")
    args = parser.parse_args()

    run_variant(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
