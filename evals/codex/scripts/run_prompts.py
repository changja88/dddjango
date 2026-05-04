#!/usr/bin/env python3
import argparse
import json
import subprocess
import time
from pathlib import Path


def extract_prompt(text):
    marker = "## Prompt"
    if marker not in text:
        return text.strip()
    return text.split(marker, 1)[1].strip()


def case_id_from_prompt_file(path):
    name = Path(path).name
    if not name.endswith(".prompt.md"):
        raise ValueError(f"not a prompt file: {path}")
    return name.removesuffix(".prompt.md")


def build_codex_command(
    *,
    prompt_file,
    output_file,
    cwd,
    variant,
    model,
    profile,
    ignore_user_config,
):
    command = [
        "codex",
        "exec",
        "--ephemeral",
        "--sandbox",
        "read-only",
        "--skip-git-repo-check",
        "--cd",
        str(cwd),
        "--output-last-message",
        str(output_file),
    ]
    if ignore_user_config:
        command.append("--ignore-user-config")
    if model:
        command.extend(["-m", model])
    if profile:
        command.extend(["--profile", profile])
    command.append(extract_prompt(Path(prompt_file).read_text()))
    return command


def load_timing(path):
    if not Path(path).exists():
        return []
    return json.loads(Path(path).read_text())


def update_timing(path, *, case_id, variant, duration_sec, model, profile, returncode):
    records = load_timing(path)
    updated = False
    for record in records:
        if record.get("case_id") == case_id and record.get("variant") == variant:
            record["duration_sec"] = round(duration_sec, 2)
            record["model"] = model or record.get("model", "")
            record["profile"] = profile
            record["returncode"] = returncode
            updated = True
            break
    if not updated:
        records.append(
            {
                "case_id": case_id,
                "variant": variant,
                "duration_sec": round(duration_sec, 2),
                "approx_tokens_in": None,
                "approx_tokens_out": None,
                "tool_calls": None,
                "model": model,
                "profile": profile,
                "returncode": returncode,
                "notes": "",
            }
        )
    Path(path).write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")


def run_variant(args):
    iteration = Path(args.iteration)
    prompt_dir = iteration / args.variant
    output_dir = prompt_dir
    timing_path = iteration / "timing.json"
    eval_cwd = Path(args.cwd)
    eval_cwd.mkdir(parents=True, exist_ok=True)

    prompt_files = sorted(prompt_dir.glob("*.prompt.md"))
    if args.case:
        prompt_files = [path for path in prompt_files if case_id_from_prompt_file(path) == args.case]
    if not prompt_files:
        raise RuntimeError(f"no prompt files found for variant {args.variant}")

    ignore_user_config = args.ignore_user_config
    if args.variant == "baseline" and not args.allow_user_config:
        ignore_user_config = True

    for prompt_file in prompt_files:
        case_id = case_id_from_prompt_file(prompt_file)
        output_file = output_dir / f"{case_id}.output.md"
        command = build_codex_command(
            prompt_file=prompt_file,
            output_file=output_file,
            cwd=eval_cwd,
            variant=args.variant,
            model=args.model,
            profile=args.profile,
            ignore_user_config=ignore_user_config,
        )

        if args.dry_run:
            print(" ".join(command))
            continue

        started = time.perf_counter()
        result = subprocess.run(command, text=True, capture_output=True)
        duration = time.perf_counter() - started
        log_file = output_dir / f"{case_id}.codex.log"
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
            profile=args.profile,
            returncode=result.returncode,
        )
        print(f"{args.variant}/{case_id}: returncode={result.returncode}")
        if result.returncode != 0 and not args.keep_going:
            raise RuntimeError(f"codex exec failed for {args.variant}/{case_id}")


def main():
    parser = argparse.ArgumentParser(
        description="Run generated Codex evaluation prompts and capture outputs."
    )
    parser.add_argument("--iteration", default="workspace/codex-eval/iteration-1")
    parser.add_argument("--variant", choices=["baseline", "dddjango"], required=True)
    parser.add_argument("--case", help="Run only one case id.")
    parser.add_argument(
        "--cwd",
        default="/private/tmp/dddjango-codex-eval",
        help="Clean cwd for codex exec. Keep it outside this repo to avoid AGENTS.md leakage.",
    )
    parser.add_argument("--model", default="")
    parser.add_argument("--profile", default="")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--keep-going", action="store_true")
    parser.add_argument(
        "--ignore-user-config",
        action="store_true",
        help="Ignore user config for this run.",
    )
    parser.add_argument(
        "--allow-user-config",
        action="store_true",
        help="Allow user config for baseline. Not recommended for clean baseline runs.",
    )
    args = parser.parse_args()

    run_variant(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
