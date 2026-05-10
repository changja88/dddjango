#!/usr/bin/env python3
"""Run dddjango eval buckets with baseline and plugin-enabled variants."""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import eval_run_common as common
import extract_subagent_trace


REPO_ROOT = common.REPO_ROOT
EVAL_ROOT = common.EVAL_ROOT
DEFAULT_WORKSPACE_ROOT = Path("/private/tmp/dddjango-eval-workspaces")
DEFAULT_MODEL = "gpt-5.5"
DEFAULT_REASONING = "xhigh"
CODE_CAPTURE_METADATA = EVAL_ROOT / "code/cases/plugin/code-capture.json"
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


VARIANT_CONFIG = {
    "baseline": Variant("baseline", ignore_user_config=True, isolated_baseline=True),
    "with-dddjango": Variant("with-dddjango", ignore_user_config=False),
}


def eval_rel_path(*parts: str) -> Path:
    return Path("workspace/develop/eval").joinpath(*parts)


def all_bucket_excluded_paths() -> list[Path]:
    paths: list[Path] = [
        Path(".git"),
        Path(".venv"),
        Path("__pycache__"),
        Path(".pytest_cache"),
        Path(".mypy_cache"),
        Path(".ruff_cache"),
    ]
    for bucket in common.BUCKETS:
        paths.append(eval_rel_path(bucket, "answer"))
        paths.append(eval_rel_path(bucket, "runs"))
        paths.append(eval_rel_path(bucket, "cases/plugin/private"))
    paths.append(eval_rel_path("source", "crosswalks"))
    return paths


ALWAYS_EXCLUDED_FROM_EVAL_WORKSPACE = all_bucket_excluded_paths()
SUBAGENT_TRACE_MARKER = "SUBAGENT_TRACE_CAPTURE.json"
BASELINE_ONLY_EXCLUDED_FROM_EVAL_WORKSPACE = [
    Path(".agents"),
    Path(".codex/plugins/cache"),
    Path(".codex/skills"),
    Path("dddjango"),
    Path("plugins"),
    eval_rel_path("source", "crosswalks"),
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bucket", choices=common.BUCKETS, required=True)
    parser.add_argument("--run-id")
    parser.add_argument("--case", action="append", help="Case id to run. Repeatable.")
    parser.add_argument("--variant", action="append", choices=common.VARIANTS)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--reasoning", default=DEFAULT_REASONING)
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    parser.add_argument("--rerun", action="store_true")
    parser.add_argument("--skip-exec", action="store_true")
    parser.add_argument("--workspace-root", type=Path, default=DEFAULT_WORKSPACE_ROOT)
    return parser.parse_args(argv)


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


def resolved_under(root: Path, *parts: str | Path, description: str) -> Path:
    root_resolved = root.resolve()
    path = root.joinpath(*parts)
    resolved = path.resolve(strict=False)
    try:
        resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise SystemExit(f"{description} escapes intended root: {path}") from exc
    return path


def now_text() -> str:
    return datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y%m%d-%H%M")


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


def validate_answer_oracles(case_files: list[Path], answer_dir: Path, bucket: str) -> None:
    for case_file in case_files:
        case_id = case_file.stem
        answer_path = answer_dir / f"{case_id}.yaml"
        text = common.read_text(answer_path)
        if not text.strip():
            raise SystemExit(f"missing or empty answer oracle for {case_id}: {answer_path}")
        case_pattern = re.compile(
            rf"(?m)^\s*case_id\s*:\s*['\"]?{re.escape(case_id)}['\"]?\s*(?:#.*)?$"
        )
        kind_pattern = re.compile(
            rf"(?m)^\s*kind\s*:\s*['\"]?{re.escape(bucket)}['\"]?\s*(?:#.*)?$"
        )
        if not case_pattern.search(text):
            raise SystemExit(f"{answer_path} must declare case_id: {case_id}")
        if not kind_pattern.search(text):
            raise SystemExit(f"{answer_path} must declare kind: {bucket}")


def build_prompt(public_packet: str, *, allow_workspace_edits: bool) -> str:
    if allow_workspace_edits:
        edit_policy = (
            "You may edit files in the current working directory to complete the user's request.\n"
            "Do not write into evaluator-only directories, private case maps, or run-output directories.\n"
            "Preserve unrelated user changes and do not revert files you did not change.\n"
        )
    else:
        edit_policy = (
            "Do not modify files. If a check is not actually run, state that it was not run.\n"
            "Preserve the current file-edit policy by avoiding writes in this read-only evaluation.\n"
        )
    return (
        "Answer the user request directly.\n"
        "Use only files in the current working directory when local files are needed.\n"
        "Do not read evaluator-only answer oracles, private case maps, prior run outputs, "
        "private scoring notes, or crosswalk files if present.\n"
        f"{edit_policy}"
        "Keep the answer concise and include commands actually run plus checks not run.\n\n"
        "----- USER REQUEST START -----\n"
        f"{public_packet.rstrip()}\n"
        "----- USER REQUEST END -----\n"
    )


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink(missing_ok=True)
    elif path.is_dir():
        shutil.rmtree(path)


def prepare_isolated_workspace(
    *,
    source_repo: Path,
    workspace_root: Path,
    run_id: str,
    case_id: str,
    variant: Variant,
) -> Path:
    workspace = resolved_under(
        workspace_root,
        run_id,
        case_id,
        variant.name,
        description="workspace path",
    )
    if workspace.exists():
        shutil.rmtree(workspace)
    ignore = shutil.ignore_patterns(
        ".git",
        ".venv",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
    )
    shutil.copytree(source_repo, workspace, symlinks=True, ignore=ignore)
    excluded = list(ALWAYS_EXCLUDED_FROM_EVAL_WORKSPACE)
    if variant.isolated_baseline:
        excluded.extend(BASELINE_ONLY_EXCLUDED_FROM_EVAL_WORKSPACE)
    for rel_path in excluded:
        remove_path(resolved_under(workspace, rel_path, description="workspace cleanup path"))
    initialize_git_snapshot(workspace)
    return workspace


def initialize_git_snapshot(workspace: Path) -> None:
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


def relative_presence(workspace: Path, rel_paths: list[Path]) -> dict[str, bool]:
    return {path.as_posix(): (workspace / path).exists() for path in rel_paths}


def baseline_forbidden_paths() -> list[Path]:
    paths = [
        Path("dddjango/skills"),
        Path("dddjango/.codex-plugin/plugin.json"),
        Path(".agents/plugins/marketplace.json"),
        Path(".codex/plugins/cache/dddjango-local"),
        Path("plugins/dddjango"),
        Path("plugins/cache/dddjango-local"),
        eval_rel_path("source", "crosswalks"),
    ]
    for bucket in common.BUCKETS:
        paths.append(eval_rel_path(bucket, "answer"))
        paths.append(eval_rel_path(bucket, "runs"))
        paths.append(eval_rel_path(bucket, "cases/plugin/private"))
    return paths


def write_baseline_isolation_artifact(
    *,
    raw_dir: Path,
    case_id: str,
    workspace: Path,
    workspace_root: Path,
    command: list[str],
    prompt: str,
) -> None:
    forbidden_rel_paths = baseline_forbidden_paths()
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
        "pass": (
            workspace.resolve() != REPO_ROOT.resolve()
            and "--ignore-user-config" in command
            and "--ignore-rules" in command
            and not any(presence.values())
            and str(REPO_ROOT) not in prompt
            and not any(marker in prompt for marker in prompt_metadata_markers)
        ),
    }
    common.write_text(
        raw_dir / f"{case_id}-baseline-isolation.json",
        json.dumps(artifact, ensure_ascii=False, indent=2) + "\n",
    )


def load_code_capture_metadata(*, required: bool) -> dict[str, object]:
    if not CODE_CAPTURE_METADATA.exists():
        if required:
            raise SystemExit(f"missing code capture metadata: {CODE_CAPTURE_METADATA}")
        return {"cases": {}}
    return json.loads(CODE_CAPTURE_METADATA.read_text(encoding="utf-8"))


def case_capture_config(metadata: dict[str, object], case_id: str) -> dict[str, object]:
    cases = metadata.get("cases")
    if not isinstance(cases, dict):
        raise SystemExit("code capture metadata must contain a cases object")
    value = cases.get(case_id)
    if not isinstance(value, dict) or value.get("captureCode") is not True:
        raise SystemExit(f"{case_id} must have captureCode: true in code-capture.json")
    if not value.get("subjectRepo"):
        raise SystemExit(f"{case_id} is code-backed but has no subjectRepo")
    return value


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


def porcelain_status(workspace: Path) -> list[tuple[str, str]]:
    result = run_command(
        ["git", "status", "--porcelain=v1", "-uall"],
        prompt=None,
        cwd=workspace,
        timeout_seconds=120,
    )
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
    staged_diff = run_command(["git", "diff", "--cached", "--binary", "--"], prompt=None, cwd=workspace, timeout_seconds=120).stdout
    unstaged_diff = run_command(["git", "diff", "--binary", "--"], prompt=None, cwd=workspace, timeout_seconds=120).stdout
    diff_parts = [staged_diff.rstrip(), unstaged_diff.rstrip()]
    manifest_files: list[dict[str, object]] = []

    for status_code, path_text in status_entries:
        rel_path = safe_relative_path(path_text)
        source_path = workspace / rel_path
        status = status_label(status_code)
        is_deleted = status == "deleted"
        binary = True if is_deleted else source_path.exists() and is_binary(source_path)
        artifact_path = Path("code") / case_id / variant / "files" / rel_path
        artifact_path_text = "" if is_deleted else artifact_path.as_posix()
        entry: dict[str, object] = {
            "path": rel_path.as_posix(),
            "status": status,
            "language": language_for_path(rel_path),
            "artifactPath": artifact_path_text,
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
    common.write_text(artifact_base / "diff.patch", diff_text + ("\n" if diff_text else ""))
    manifest = {
        "caseId": case_id,
        "variant": variant,
        "workspace": str(workspace),
        "evidenceMode": "code-backed",
        "diffPath": f"code/{case_id}/{variant}/diff.patch",
        "noCodeProduced": not manifest_files,
        "files": manifest_files,
    }
    common.write_text(
        artifact_base / "changed-files.json",
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
    )


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
        "--json",
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
        command.extend(["--ignore-user-config", "--ignore-rules"])
    command.append("-")
    return command


def write_command_artifact(path: Path, command: list[str]) -> None:
    common.write_text(path, shlex.join(command) + "\n")


def write_subagent_trace_marker(run_dir: Path, bucket: str) -> None:
    if bucket != "workflow":
        return
    marker = {
        "version": 1,
        "bucket": bucket,
        "createdBy": "run_eval_bucket.py",
        "tracePolicy": extract_subagent_trace.TRACE_CAPTURE_POLICY,
        "stderrUsedForClaims": False,
    }
    common.write_text(
        run_dir / SUBAGENT_TRACE_MARKER,
        json.dumps(marker, ensure_ascii=False, indent=2) + "\n",
    )


def trace_artifact_path(raw_dir: Path, case_id: str, variant: str) -> Path:
    return raw_dir / f"{case_id}-{variant}-subagent-trace.json"


def write_workflow_trace_artifact(
    *,
    bucket: str,
    run_dir: Path,
    raw_dir: Path,
    case_id: str,
    variant: str,
    skipped: bool,
) -> None:
    if bucket != "workflow":
        return
    extract_subagent_trace.write_trace_summary(
        output_path=trace_artifact_path(raw_dir, case_id, variant),
        case_id=case_id,
        variant=variant,
        run_dir=run_dir,
        response_path=raw_dir / f"{case_id}-{variant}.txt",
        event_path=raw_dir / f"{case_id}-{variant}-events.jsonl",
        skipped=skipped,
    )


def clean_forbidden_prompt_input_artifacts(raw_dir: Path, case_id: str) -> None:
    for suffix in (
        "prompt-input.json",
        "prompt-input.stderr.txt",
        "baseline-prompt-input.json",
        "baseline-prompt-input.stderr.txt",
    ):
        (raw_dir / f"{case_id}-{suffix}").unlink(missing_ok=True)


def debug_prompt_input(case_id: str, raw_dir: Path, prompt: str, timeout_seconds: int) -> None:
    prompt_input_path = raw_dir / f"{case_id}-with-dddjango-prompt-input.json"
    debug_result = run_command(
        ["codex", "debug", "prompt-input", prompt],
        prompt=None,
        cwd=REPO_ROOT,
        timeout_seconds=timeout_seconds,
    )
    common.write_text(prompt_input_path, debug_result.stdout)
    common.write_text(raw_dir / f"{case_id}-with-dddjango-prompt-input.stderr.txt", debug_result.stderr)


def write_skipped_prompt_input(case_id: str, raw_dir: Path) -> None:
    common.write_text(
        raw_dir / f"{case_id}-with-dddjango-prompt-input.json",
        json.dumps({"skipped": True, "reason": "--skip-exec"}, ensure_ascii=False) + "\n",
    )
    common.write_text(raw_dir / f"{case_id}-with-dddjango-prompt-input.stderr.txt", "")


def should_skip_existing_output(
    *,
    output_path: Path,
    exit_path: Path,
    current_skip_exec: bool,
    rerun: bool,
) -> bool:
    if rerun or not output_path.exists() or output_path.stat().st_size == 0:
        return False
    previous_exit = common.read_text(exit_path).strip()
    if not current_skip_exec and previous_exit == "skipped":
        return False
    return True


def response_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def selected_variants(raw_names: list[str] | None) -> list[Variant]:
    names = raw_names or list(common.VARIANTS)
    return [VARIANT_CONFIG[name] for name in names]


def workspace_for_case_variant(
    *,
    bucket: str,
    code_capture_config: dict[str, object] | None,
    workspace_root: Path,
    run_id: str,
    case_id: str,
    variant: Variant,
) -> tuple[Path, str]:
    if bucket == "code":
        assert code_capture_config is not None
        configured_subject = Path(str(code_capture_config["subjectRepo"]))
        source_repo = configured_subject if configured_subject.is_absolute() else REPO_ROOT / configured_subject
        if not source_repo.is_dir():
            raise SystemExit(f"subject repo does not exist: {source_repo}")
        workspace = prepare_isolated_workspace(
            source_repo=source_repo,
            workspace_root=workspace_root,
            run_id=run_id,
            case_id=case_id,
            variant=variant,
        )
        return workspace, "workspace-write"
    workspace = prepare_isolated_workspace(
        source_repo=REPO_ROOT,
        workspace_root=workspace_root,
        run_id=run_id,
        case_id=case_id,
        variant=variant,
    )
    return workspace, "read-only"


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    run_id = validate_run_id(args.run_id or f"{now_text()}-{args.bucket}-eval")
    bucket = common.bucket_paths(args.bucket)
    cases = common.selected_case_paths(args.bucket, args.case)
    variants = selected_variants(args.variant)
    validate_answer_oracles(cases, bucket.answer_dir, args.bucket)
    code_metadata = load_code_capture_metadata(required=args.bucket == "code")

    run_dir = resolved_under(bucket.runs_dir, run_id, description="run path")
    raw_dir = run_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    common.write_text(run_dir / "RUN_ID.txt", run_id + "\n")
    write_subagent_trace_marker(run_dir, args.bucket)

    for case_path in cases:
        case_id = case_path.stem
        public_packet = common.read_text(case_path)
        code_config = case_capture_config(code_metadata, case_id) if args.bucket == "code" else None
        prompt = build_prompt(public_packet, allow_workspace_edits=args.bucket == "code")

        shutil.copyfile(case_path, raw_dir / f"{case_id}-public-prompt.md")
        common.write_text(raw_dir / f"{case_id}-operator-prompt.txt", prompt)
        clean_forbidden_prompt_input_artifacts(raw_dir, case_id)
        if args.skip_exec:
            write_skipped_prompt_input(case_id, raw_dir)
        else:
            debug_prompt_input(case_id, raw_dir, prompt, args.timeout_seconds)

        for variant in variants:
            output_path = raw_dir / f"{case_id}-{variant.name}.txt"
            stdout_path = raw_dir / f"{case_id}-{variant.name}-events.jsonl"
            stderr_path = raw_dir / f"{case_id}-{variant.name}.stderr.txt"
            command_path = raw_dir / f"{case_id}-{variant.name}-command.txt"
            exit_path = raw_dir / f"{case_id}-{variant.name}-exit.txt"

            if should_skip_existing_output(
                output_path=output_path,
                exit_path=exit_path,
                current_skip_exec=args.skip_exec,
                rerun=args.rerun,
            ):
                print(f"skip existing {case_id} {variant.name}")
                if args.bucket == "workflow" and not trace_artifact_path(
                    raw_dir, case_id, variant.name
                ).is_file():
                    skipped = common.read_text(exit_path).strip() == "skipped"
                    write_workflow_trace_artifact(
                        bucket=args.bucket,
                        run_dir=run_dir,
                        raw_dir=raw_dir,
                        case_id=case_id,
                        variant=variant.name,
                        skipped=skipped,
                    )
                continue

            exec_cwd, sandbox = workspace_for_case_variant(
                bucket=args.bucket,
                code_capture_config=code_config,
                workspace_root=args.workspace_root,
                run_id=run_id,
                case_id=case_id,
                variant=variant,
            )
            command = codex_exec_command(
                variant,
                output_path=output_path,
                model=args.model,
                reasoning=args.reasoning,
                cwd=exec_cwd,
                sandbox=sandbox,
            )
            write_command_artifact(command_path, command)
            if variant.isolated_baseline:
                write_baseline_isolation_artifact(
                    raw_dir=raw_dir,
                    case_id=case_id,
                    workspace=exec_cwd,
                    workspace_root=args.workspace_root,
                    command=command,
                    prompt=prompt,
                )

            if args.skip_exec:
                common.write_text(output_path, "NOT RUN: --skip-exec was used.\n")
                common.write_text(stdout_path, "")
                common.write_text(stderr_path, "")
                common.write_text(exit_path, "skipped\n")
                if args.bucket == "code":
                    capture_code_artifacts(exec_cwd, run_dir, case_id, variant.name)
                write_workflow_trace_artifact(
                    bucket=args.bucket,
                    run_dir=run_dir,
                    raw_dir=raw_dir,
                    case_id=case_id,
                    variant=variant.name,
                    skipped=True,
                )
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
                common.write_text(stdout_path, response_text(exc.stdout))
                common.write_text(stderr_path, response_text(exc.stderr))
                common.write_text(exit_path, f"timeout after {args.timeout_seconds}s\n")
                if not output_path.exists():
                    common.write_text(output_path, "")
                write_workflow_trace_artifact(
                    bucket=args.bucket,
                    run_dir=run_dir,
                    raw_dir=raw_dir,
                    case_id=case_id,
                    variant=variant.name,
                    skipped=False,
                )
                continue

            common.write_text(stdout_path, result.stdout)
            common.write_text(stderr_path, result.stderr)
            common.write_text(exit_path, str(result.returncode) + "\n")
            if not output_path.exists():
                common.write_text(output_path, "")
            if args.bucket == "code":
                capture_code_artifacts(exec_cwd, run_dir, case_id, variant.name)
            write_workflow_trace_artifact(
                bucket=args.bucket,
                run_dir=run_dir,
                raw_dir=raw_dir,
                case_id=case_id,
                variant=variant.name,
                skipped=False,
            )

    return 0


if __name__ == "__main__":
    sys.exit(main())
