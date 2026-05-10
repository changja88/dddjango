#!/usr/bin/env python3
"""Run dddjango plugin eval public packets with and without the plugin config."""

from __future__ import annotations

import argparse
import json
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
CODE_CAPTURE_METADATA = REPO_ROOT / "workspace/develop/evals/cases/plugin/code-capture.json"
RUNS_DIR = REPO_ROOT / "workspace/develop/evals/runs"
DEFAULT_WORKSPACE_ROOT = Path("/private/tmp/dddjango-eval-workspaces")
DEFAULT_MODEL = "gpt-5.5"
DEFAULT_REASONING = "xhigh"
TEXT_SUFFIX_LANGUAGES = {
    ".css": "css",
    ".html": "html",
    ".js": "javascript",
    ".json": "json",
    ".md": "markdown",
    ".py": "python",
    ".sql": "sql",
    ".toml": "toml",
    ".ts": "typescript",
    ".txt": "text",
    ".yaml": "yaml",
    ".yml": "yaml",
}


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
    parser.add_argument("--capture-code", action="store_true", help="Run code-backed cases in isolated workspaces.")
    parser.add_argument("--workspace-root", type=Path, default=DEFAULT_WORKSPACE_ROOT)
    parser.add_argument("--subject-repo", type=Path, help="Override the fixture/source repo for code capture.")
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


def load_code_capture_metadata() -> dict[str, object]:
    if not CODE_CAPTURE_METADATA.exists():
        return {"cases": {}}
    return json.loads(CODE_CAPTURE_METADATA.read_text(encoding="utf-8"))


def case_capture_config(metadata: dict[str, object], case_id: str) -> dict[str, object]:
    cases = metadata.get("cases")
    if not isinstance(cases, dict):
        return {}
    value = cases.get(case_id, {})
    return value if isinstance(value, dict) else {}


def build_prompt(public_packet: str, *, allow_workspace_edits: bool) -> str:
    edit_policy = (
        "You may edit files in the task workspace to complete this eval case.\n"
        "Do not write into workspace/develop/evals, workspace/develop/rubrics, or private eval paths.\n"
        if allow_workspace_edits
        else "Do not modify files. If a check is not actually run, state that it was not run.\n"
    )
    return (
        "You are executing a public forward-eval packet for the dddjango plugin.\n"
        "Use only the public packet below and task-local repository files if needed.\n"
        "Do not read workspace/develop/rubrics, workspace/develop/evals/cases/plugin/private, "
        "prior run reports, or prior findings.\n"
        f"{edit_policy}"
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


def is_binary(path: Path) -> bool:
    try:
        return b"\0" in path.read_bytes()[:8192]
    except OSError:
        return True


def language_for_path(path: Path) -> str:
    return TEXT_SUFFIX_LANGUAGES.get(path.suffix.lower(), "text")


def safe_relative_path(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"unsafe changed path: {path_text}")
    return path


def prepare_workspace(source_repo: Path, workspace_root: Path, run_id: str, case_id: str, variant: str) -> Path:
    workspace = workspace_root / run_id / case_id / variant
    if workspace.exists():
        shutil.rmtree(workspace)
    ignore = shutil.ignore_patterns(
        ".git",
        ".venv",
        "__pycache__",
        ".pytest_cache",
        "workspace/develop/evals/runs",
    )
    shutil.copytree(source_repo, workspace, ignore=ignore)
    run_command(["git", "init"], prompt=None, cwd=workspace, timeout_seconds=120)
    run_command(["git", "add", "."], prompt=None, cwd=workspace, timeout_seconds=120)
    run_command(
        [
            "git",
            "-c",
            "user.name=dddjango Eval",
            "-c",
            "user.email=eval@example.invalid",
            "commit",
            "-m",
            "eval fixture baseline",
        ],
        prompt=None,
        cwd=workspace,
        timeout_seconds=120,
    )
    return workspace


def porcelain_status(workspace: Path) -> list[tuple[str, str]]:
    result = run_command(["git", "status", "--porcelain=v1"], prompt=None, cwd=workspace, timeout_seconds=120)
    entries: list[tuple[str, str]] = []
    for line in result.stdout.splitlines():
        if not line:
            continue
        status = line[:2]
        raw_path = line[3:]
        path = raw_path.split(" -> ")[-1] if " -> " in raw_path else raw_path
        entries.append((status, path))
    return entries


def status_label(status_code: str) -> str:
    if status_code == "??":
        return "untracked"
    if "D" in status_code:
        return "deleted"
    if "A" in status_code:
        return "added"
    if "R" in status_code:
        return "renamed"
    return "modified"


def untracked_diff(workspace: Path, path: Path) -> str:
    if is_binary(workspace / path):
        return f"\nBinary file {path.as_posix()} added; no text diff captured.\n"
    result = run_command(
        ["git", "diff", "--no-index", "--", "/dev/null", path.as_posix()],
        prompt=None,
        cwd=workspace,
        timeout_seconds=120,
    )
    return result.stdout + result.stderr


def capture_code_artifacts(workspace: Path, run_dir: Path, case_id: str, variant: str) -> None:
    artifact_base = run_dir / "code" / case_id / variant
    files_base = artifact_base / "files"
    files_base.mkdir(parents=True, exist_ok=True)

    status_entries = porcelain_status(workspace)
    unstaged_diff = run_command(
        ["git", "diff", "--binary", "--"],
        prompt=None,
        cwd=workspace,
        timeout_seconds=120,
    ).stdout
    staged_diff = run_command(
        ["git", "diff", "--cached", "--binary", "--"],
        prompt=None,
        cwd=workspace,
        timeout_seconds=120,
    ).stdout
    diff_parts = [staged_diff.rstrip(), unstaged_diff.rstrip()]
    manifest_files: list[dict[str, object]] = []

    for status_code, path_text in status_entries:
        rel_path = safe_relative_path(path_text)
        source_path = workspace / rel_path
        status = status_label(status_code)
        binary = source_path.exists() and is_binary(source_path)
        artifact_path = Path("code") / case_id / variant / "files" / rel_path
        entry: dict[str, object] = {
            "path": rel_path.as_posix(),
            "status": status,
            "language": language_for_path(rel_path),
            "artifactPath": artifact_path.as_posix(),
            "lineCount": 0,
            "byteCount": 0,
            "binary": binary,
        }
        if source_path.exists() and not binary:
            target_path = files_base / rel_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_path, target_path)
            content = target_path.read_text(encoding="utf-8", errors="replace")
            entry["lineCount"] = len(content.splitlines())
            entry["byteCount"] = len(content.encode("utf-8"))
            if status == "untracked":
                diff_parts.append(untracked_diff(workspace, rel_path).rstrip())
        manifest_files.append(entry)

    diff_text = "\n".join(part for part in diff_parts if part).strip()
    (artifact_base / "diff.patch").write_text(diff_text + ("\n" if diff_text else ""), encoding="utf-8")
    manifest = {
        "caseId": case_id,
        "variant": variant,
        "workspace": str(workspace),
        "evidenceMode": "code-backed",
        "diffPath": f"code/{case_id}/{variant}/diff.patch",
        "noCodeProduced": not manifest_files,
        "files": manifest_files,
    }
    write_text(artifact_base / "changed-files.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")


def codex_exec_command(
    variant: Variant,
    *,
    output_path: Path,
    model: str,
    reasoning: str,
    cwd: Path,
    sandbox: str,
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
        str(cwd),
        "-s",
        sandbox,
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
    code_capture_metadata = load_code_capture_metadata()

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
        capture_config = case_capture_config(code_capture_metadata, case_id)
        should_capture_code = bool(args.capture_code and capture_config.get("captureCode"))
        public_packet = case_path.read_text(encoding="utf-8")
        prompt = build_prompt(public_packet, allow_workspace_edits=should_capture_code)
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
            exec_cwd = REPO_ROOT
            sandbox = "read-only"
            if should_capture_code:
                configured_subject = args.subject_repo or Path(str(capture_config.get("subjectRepo", "")))
                if not configured_subject:
                    raise SystemExit(f"{case_id} is code-backed but has no subjectRepo")
                subject_repo = configured_subject if configured_subject.is_absolute() else REPO_ROOT / configured_subject
                if not subject_repo.is_dir():
                    raise SystemExit(f"subject repo does not exist: {subject_repo}")
                exec_cwd = prepare_workspace(subject_repo, args.workspace_root, run_id, case_id, variant.name)
                sandbox = "workspace-write"
            command = codex_exec_command(
                variant,
                output_path=output_path,
                model=args.model,
                reasoning=args.reasoning,
                cwd=exec_cwd,
                sandbox=sandbox,
            )
            write_text(command_path, " ".join(command) + "\n")
            if args.skip_exec:
                write_text(output_path, "NOT RUN: --skip-exec was used.\n")
                write_text(exit_path, "skipped\n")
                if should_capture_code:
                    capture_code_artifacts(exec_cwd, run_dir, case_id, variant.name)
                continue
            print(f"run {case_id} {variant.name}", flush=True)
            try:
                result = run_command(
                    command,
                    prompt=prompt,
                    cwd=exec_cwd,
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
            if should_capture_code:
                capture_code_artifacts(exec_cwd, run_dir, case_id, variant.name)

    return 0


if __name__ == "__main__":
    sys.exit(main())
