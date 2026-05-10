#!/usr/bin/env python3
"""Run dddjango plugin eval public packets with and without the plugin config."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


REPO_ROOT = Path("/Users/hyun/Desktop/dddjango")
PUBLIC_CASES = REPO_ROOT / "workspace/develop/eval/response/cases/plugin/public"
CODE_PUBLIC_CASES = REPO_ROOT / "workspace/develop/eval/code/cases/plugin/public"
RESPONSE_ANSWER = REPO_ROOT / "workspace/develop/eval/response/answer"
CODE_ANSWER = REPO_ROOT / "workspace/develop/eval/code/answer"
CODE_CAPTURE_METADATA = REPO_ROOT / "workspace/develop/eval/code/cases/plugin/code-capture.json"
RESPONSE_RUNS_DIR = REPO_ROOT / "workspace/develop/eval/response/runs"
CODE_RUNS_DIR = REPO_ROOT / "workspace/develop/eval/code/runs"
DEFAULT_WORKSPACE_ROOT = Path("/private/tmp/dddjango-eval-workspaces")
DEFAULT_MODEL = "gpt-5.5"
DEFAULT_REASONING = "xhigh"
EVAL_BUCKETS = ("code", "plugin", "response", "runtime", "source", "workflow")
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
    isolated_baseline: bool = False


VARIANTS = {
    "baseline": Variant("baseline", True, True),
    "with-dddjango": Variant("with-dddjango", False),
}

ALWAYS_EXCLUDED_FROM_EVAL_WORKSPACE = [
    Path(".git"),
    Path(".venv"),
    Path("__pycache__"),
    Path(".pytest_cache"),
    *(Path(f"workspace/develop/eval/{bucket}/answer") for bucket in EVAL_BUCKETS),
    Path("workspace/develop/eval/code/runs"),
    Path("workspace/develop/eval/plugin/runs"),
    Path("workspace/develop/eval/response/runs"),
    Path("workspace/develop/eval/response/cases/plugin/private"),
    Path("workspace/develop/eval/runtime/runs"),
    Path("workspace/develop/eval/source/runs"),
    Path("workspace/develop/eval/workflow/runs"),
]

BASELINE_ONLY_EXCLUDED_FROM_EVAL_WORKSPACE = [
    Path(".agents"),
    Path("plugins"),
    Path("dddjango"),
    Path("workspace/develop/eval/source/crosswalks"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", help="Existing or new run id. Defaults to timestamped id.")
    parser.add_argument("--case", action="append", help="Case id to run, e.g. case-003. Repeatable.")
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


def case_paths(selected: list[str] | None, *, capture_code: bool) -> list[Path]:
    paths = sorted((CODE_PUBLIC_CASES if capture_code else PUBLIC_CASES).glob("case-*.md"))
    if not selected:
        if not paths:
            raise SystemExit(
                f"No public cases found in {CODE_PUBLIC_CASES if capture_code else PUBLIC_CASES}"
            )
        return paths
    wanted = set(selected)
    found = {path.stem for path in paths}
    missing = sorted(wanted - found)
    if missing:
        other_root = PUBLIC_CASES if capture_code else CODE_PUBLIC_CASES
        other_ids = {path.stem for path in other_root.glob("case-*.md")}
        wrong_mode = sorted(set(missing) & other_ids)
        if wrong_mode:
            required = "--capture-code" if not capture_code else "response mode without --capture-code"
            raise SystemExit(f"Case id(s) require {required}: {', '.join(wrong_mode)}")
        raise SystemExit(f"Unknown case id(s): {', '.join(missing)}")
    return [path for path in paths if path.stem in wanted]


def validate_answer_oracles(case_files: list[Path], answer_dir: Path, *, kind: str) -> None:
    for case_file in case_files:
        case_id = case_file.stem
        answer_path = answer_dir / f"{case_id}.yaml"
        try:
            text = answer_path.read_text(encoding="utf-8")
        except FileNotFoundError as exc:
            raise SystemExit(f"missing answer oracle for {case_id}: {answer_path}") from exc
        if not text.strip():
            raise SystemExit(f"empty answer oracle for {case_id}: {answer_path}")
        case_pattern = re.compile(
            rf"(?m)^\s*case_id\s*:\s*['\"]?{re.escape(case_id)}['\"]?\s*(?:#.*)?$"
        )
        kind_pattern = re.compile(
            rf"(?m)^\s*kind\s*:\s*['\"]?{re.escape(kind)}['\"]?\s*(?:#.*)?$"
        )
        if not case_pattern.search(text):
            raise SystemExit(f"{answer_path} must declare case_id: {case_id}")
        if not kind_pattern.search(text):
            raise SystemExit(f"{answer_path} must declare kind: {kind}")


def load_code_capture_metadata(*, required: bool) -> dict[str, object]:
    if not CODE_CAPTURE_METADATA.exists():
        if required:
            raise SystemExit(f"missing code capture metadata: {CODE_CAPTURE_METADATA}")
        return {"cases": {}}
    return json.loads(CODE_CAPTURE_METADATA.read_text(encoding="utf-8"))


def case_capture_config(metadata: dict[str, object], case_id: str, *, required: bool = False) -> dict[str, object]:
    cases = metadata.get("cases")
    if not isinstance(cases, dict):
        if required:
            raise SystemExit("code capture metadata must contain a cases object")
        return {}
    value = cases.get(case_id, {})
    if not isinstance(value, dict):
        if required:
            raise SystemExit(f"code capture metadata for {case_id} must be an object")
        return {}
    if required and not value.get("captureCode"):
        raise SystemExit(f"{case_id} must have captureCode: true for --capture-code")
    return value


def build_prompt(public_packet: str, *, allow_workspace_edits: bool) -> str:
    edit_policy = (
        "You may edit files in the current working directory to complete the user's request.\n"
        "Do not write into eval-private or run-output directories if they exist.\n"
        if allow_workspace_edits
        else "Do not modify files. If a check is not actually run, state that it was not run.\n"
    )
    return (
        "Answer the user request directly.\n"
        "Use only files in the current working directory when local files are needed.\n"
        "Do not read evaluator-only answer oracles, private case maps, prior run outputs, or prior findings if present.\n"
        f"{edit_policy}"
        "Keep the answer concise and include commands actually run plus checks not run.\n\n"
        "----- USER REQUEST START -----\n"
        f"{public_packet.rstrip()}\n"
        "----- USER REQUEST END -----\n"
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
        "workspace/develop/eval/response/runs",
    )
    shutil.copytree(source_repo, workspace, symlinks=True, ignore=ignore)
    for rel_path in ALWAYS_EXCLUDED_FROM_EVAL_WORKSPACE:
        remove_path(workspace / rel_path)
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


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink(missing_ok=True)
    elif path.is_dir():
        shutil.rmtree(path)


def prepare_eval_workspace(
    source_repo: Path,
    workspace_root: Path,
    run_id: str,
    case_id: str,
    variant: Variant,
) -> Path:
    workspace = workspace_root / run_id / case_id / variant.name
    if workspace.exists():
        shutil.rmtree(workspace)
    ignore = shutil.ignore_patterns(
        ".git",
        ".venv",
        "__pycache__",
        ".pytest_cache",
    )
    shutil.copytree(source_repo, workspace, symlinks=True, ignore=ignore)
    excluded = list(ALWAYS_EXCLUDED_FROM_EVAL_WORKSPACE)
    if variant.isolated_baseline:
        excluded.extend(BASELINE_ONLY_EXCLUDED_FROM_EVAL_WORKSPACE)
    for rel_path in excluded:
        remove_path(workspace / rel_path)
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
            "eval sanitized workspace",
        ],
        prompt=None,
        cwd=workspace,
        timeout_seconds=120,
    )
    return workspace


def relative_presence(workspace: Path, rel_paths: list[Path]) -> dict[str, bool]:
    return {path.as_posix(): (workspace / path).exists() for path in rel_paths}


def write_baseline_isolation_artifact(
    *,
    run_dir: Path,
    raw_dir: Path,
    case_id: str,
    workspace: Path,
    workspace_root: Path,
    command: list[str],
    prompt: str,
) -> None:
    forbidden_rel_paths = [
        Path("dddjango/skills"),
        Path("dddjango/.codex-plugin/plugin.json"),
        Path(".agents/plugins/marketplace.json"),
        Path("plugins/dddjango"),
        *(Path(f"workspace/develop/eval/{bucket}/answer") for bucket in EVAL_BUCKETS),
        Path("workspace/develop/eval/response/cases/plugin/private"),
        Path("workspace/develop/eval/response/runs"),
        Path("workspace/develop/eval/code/runs"),
        Path("workspace/develop/eval/plugin/runs"),
        Path("workspace/develop/eval/runtime/runs"),
        Path("workspace/develop/eval/source/crosswalks"),
        Path("workspace/develop/eval/source/runs"),
        Path("workspace/develop/eval/workflow/runs"),
    ]
    presence = relative_presence(workspace, forbidden_rel_paths)
    prompt_metadata_markers = [
        "dddjango:implementation-django",
        "dddjango:implementation-django-ninja",
        "dddjango:implementation-django-web",
        "dddjango:implementation-python",
        "dddjango:implementation-cleancode",
        "dddjango:implementation-tdd",
        "dddjango:implementation-test",
        "dddjango:architecture-ddd",
        "dddjango:architecture-implementation-patterns",
        "dddjango:architecture-db",
        "dddjango:architecture-api",
        "dddjango:workflow-dddjango-subagents",
    ]
    artifact = {
        "caseId": case_id,
        "variant": "baseline",
        "evidenceMode": "baseline-isolation",
        "workspace": str(workspace),
        "workspaceUnderEvalRoot": str(workspace).startswith(str(workspace_root)),
        "originalRepoRoot": str(REPO_ROOT),
        "runsFromOriginalRepoRoot": workspace.resolve() == REPO_ROOT.resolve(),
        "commandUsesIgnoreUserConfig": "--ignore-user-config" in command,
        "commandUsesIgnoreRules": "--ignore-rules" in command,
        "forbiddenPathPresence": presence,
        "forbiddenPathsAbsent": not any(presence.values()),
        "operatorPromptContainsOriginalRepoRoot": str(REPO_ROOT) in prompt,
        "operatorPromptDddjangoSkillMetadataMentions": [
            marker for marker in prompt_metadata_markers if marker in prompt
        ],
        "baselinePromptInputPolicy": (
            "The runner does not create active-user-config prompt-input artifacts for baseline. "
            "Baseline evidence is command isolation plus sanitized workspace absence checks."
        ),
        "runtimeCachePathNotMountedInWorkspace": not (
            workspace / "Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10"
        ).exists(),
        "pass": (
            workspace.resolve() != REPO_ROOT.resolve()
            and "--ignore-user-config" in command
            and "--ignore-rules" in command
            and not any(presence.values())
            and str(REPO_ROOT) not in prompt
            and not any(marker in prompt for marker in prompt_metadata_markers)
        ),
    }
    write_text(
        raw_dir / f"{case_id}-baseline-isolation.json",
        json.dumps(artifact, ensure_ascii=False, indent=2) + "\n",
    )


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
        command.append("--ignore-rules")
    command.append("-")
    return command


def main() -> int:
    args = parse_args()
    run_id = args.run_id or f"{now_text()}-plugin-eval"
    runs_dir = CODE_RUNS_DIR if args.capture_code else RESPONSE_RUNS_DIR
    run_dir = runs_dir / run_id
    raw_dir = run_dir / "raw"
    analysis_dir = run_dir / "analysis"
    cases = case_paths(args.case, capture_code=args.capture_code)
    variants = [VARIANTS[name] for name in (args.variant or ["baseline", "with-dddjango"])]
    validate_answer_oracles(
        cases,
        CODE_ANSWER if args.capture_code else RESPONSE_ANSWER,
        kind="code" if args.capture_code else "response",
    )
    code_capture_metadata = load_code_capture_metadata(required=args.capture_code)

    raw_dir.mkdir(parents=True, exist_ok=True)
    analysis_dir.mkdir(parents=True, exist_ok=True)

    write_text(run_dir / "RUN_ID.txt", run_id + "\n")
    for case_path in cases:
        case_id = case_path.stem
        capture_config = case_capture_config(code_capture_metadata, case_id, required=args.capture_code)
        should_capture_code = bool(args.capture_code and capture_config.get("captureCode"))
        if args.capture_code and not (args.subject_repo or capture_config.get("subjectRepo")):
            raise SystemExit(f"{case_id} is code-backed but has no subjectRepo")
        public_packet = case_path.read_text(encoding="utf-8")
        prompt = build_prompt(public_packet, allow_workspace_edits=should_capture_code)
        shutil.copyfile(case_path, raw_dir / f"{case_id}-public-prompt.md")
        write_text(raw_dir / f"{case_id}-operator-prompt.txt", prompt)

        prompt_input_path = raw_dir / f"{case_id}-with-dddjango-prompt-input.json"
        if args.rerun or not prompt_input_path.exists():
            debug_result = run_command(
                ["codex", "debug", "prompt-input", prompt],
                prompt=None,
                cwd=REPO_ROOT,
                timeout_seconds=args.timeout_seconds,
            )
            write_text(prompt_input_path, debug_result.stdout)
            write_text(raw_dir / f"{case_id}-with-dddjango-prompt-input.stderr.txt", debug_result.stderr)

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
            else:
                exec_cwd = prepare_eval_workspace(REPO_ROOT, args.workspace_root, run_id, case_id, variant)
            command = codex_exec_command(
                variant,
                output_path=output_path,
                model=args.model,
                reasoning=args.reasoning,
                cwd=exec_cwd,
                sandbox=sandbox,
            )
            write_text(command_path, " ".join(command) + "\n")
            if variant.isolated_baseline:
                write_baseline_isolation_artifact(
                    run_dir=run_dir,
                    raw_dir=raw_dir,
                    case_id=case_id,
                    workspace=exec_cwd,
                    workspace_root=args.workspace_root,
                    command=command,
                    prompt=prompt,
                )
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
