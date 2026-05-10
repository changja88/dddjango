#!/usr/bin/env python3
"""Validate completed dddjango eval run artifact sets."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import eval_run_common as common


REPO_ROOT = common.REPO_ROOT
EVAL_ROOT = common.EVAL_ROOT
CODE_CAPTURE_METADATA = EVAL_ROOT / "code/cases/plugin/code-capture.json"
SUBAGENT_TRACE_MARKER = "SUBAGENT_TRACE_CAPTURE.json"

BASELINE_CONTAMINATION_PATTERNS = {
    "dddjango marker": re.compile(
        r"(dddjango:|dddjango/skills|\.codex/plugins/cache/dddjango-local|"
        r"plugins/cache/dddjango-local|plugins/dddjango|workflow-dddjango|"
        r"architecture-ddd|implementation-django|source/crosswalks)",
        re.I,
    ),
    "evaluator-only artifact marker": re.compile(
        r"(answer-oracle|cases/plugin/private|workspace/develop/eval/[^/\s]+/(answer|runs))",
        re.I,
    ),
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bucket", choices=common.BUCKETS, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--case", action="append", help="Case id to validate. Repeatable.")
    parser.add_argument("--variant", action="append", choices=common.VARIANTS)
    parser.add_argument("--skip-oracle", action="store_true")
    parser.add_argument("--allow-skipped-exits", action="store_true")
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


def selected_variants(raw_names: list[str] | None) -> list[str]:
    return raw_names or list(common.VARIANTS)


def load_json_object(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, f"missing JSON artifact: {path}"
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON in {path}: {exc}"
    if not isinstance(value, dict):
        return None, f"{path} must contain a JSON object"
    return value, None


def yaml_has_scalar(text: str, key: str, expected: str) -> bool:
    pattern = re.compile(
        rf"(?m)^\s*{re.escape(key)}\s*:\s*['\"]?{re.escape(expected)}['\"]?\s*(?:#.*)?$"
    )
    return bool(pattern.search(text))


def validate_answer_yaml(answer_dir: Path, case_id: str, bucket: str) -> list[str]:
    findings: list[str] = []
    path = answer_dir / f"{case_id}.yaml"
    if not path.is_file():
        return [f"missing answer YAML: {path}"]
    text = path.read_text(encoding="utf-8", errors="replace")
    for key, expected in (("case_id", case_id), ("bucket", bucket), ("kind", bucket)):
        if not yaml_has_scalar(text, key, expected):
            findings.append(f"{path}: missing matching {key}: {expected}")
    return findings


def require_file(findings: list[str], path: Path, description: str) -> bool:
    if not path.is_file():
        findings.append(f"missing {description}: {path}")
        return False
    return True


def validate_common_run_artifacts(
    *,
    run_dir: Path,
    raw_dir: Path,
    case_id: str,
    variants: list[str],
    allow_skipped_exits: bool,
) -> list[str]:
    findings: list[str] = []
    require_file(findings, raw_dir / f"{case_id}-public-prompt.md", "public prompt artifact")
    require_file(findings, raw_dir / f"{case_id}-operator-prompt.txt", "operator prompt artifact")

    for suffix in ("prompt-input.json", "prompt-input.stderr.txt"):
        path = raw_dir / f"{case_id}-{suffix}"
        if path.exists():
            findings.append(f"stale unscoped prompt-input artifact must be removed: {path}")
    for suffix in ("baseline-prompt-input.json", "baseline-prompt-input.stderr.txt"):
        path = raw_dir / f"{case_id}-{suffix}"
        if path.exists():
            findings.append(f"baseline prompt-input artifact is forbidden: {path}")

    if "with-dddjango" in variants:
        for suffix in ("prompt-input.json", "prompt-input.stderr.txt"):
            require_file(
                findings,
                raw_dir / f"{case_id}-with-dddjango-{suffix}",
                "with-ddjango prompt-input artifact",
            )

    for variant in variants:
        for suffix, description in (
            (".txt", f"{variant} response artifact"),
            ("-events.jsonl", f"{variant} events artifact"),
            (".stderr.txt", f"{variant} stderr artifact"),
            ("-command.txt", f"{variant} command artifact"),
            ("-exit.txt", f"{variant} exit artifact"),
        ):
            require_file(findings, raw_dir / f"{case_id}-{variant}{suffix}", description)
        exit_path = raw_dir / f"{case_id}-{variant}-exit.txt"
        if exit_path.is_file():
            exit_text = exit_path.read_text(encoding="utf-8", errors="replace")
            allowed_exits = {"0"}
            if allow_skipped_exits:
                allowed_exits.add("skipped")
            if exit_text.strip() not in allowed_exits:
                findings.append(f"{case_id} {variant} exit is not 0: {exit_text.strip()}")

    if "baseline" in variants:
        findings.extend(validate_baseline_isolation(raw_dir, case_id))
        findings.extend(validate_baseline_output(raw_dir, case_id, run_dir))
    return findings


def validate_baseline_isolation(raw_dir: Path, case_id: str) -> list[str]:
    path = raw_dir / f"{case_id}-baseline-isolation.json"
    artifact, error = load_json_object(path)
    if error is not None:
        return [f"{case_id}: {error}"]
    assert artifact is not None

    findings: list[str] = []
    expected_values = {
        "caseId": case_id,
        "variant": "baseline",
        "evidenceMode": "baseline-isolation",
        "pass": True,
        "forbiddenPathsAbsent": True,
        "commandUsesIgnoreUserConfig": True,
        "commandUsesIgnoreRules": True,
        "runsFromOriginalRepoRoot": False,
        "operatorPromptContainsOriginalRepoRoot": False,
    }
    for key, expected in expected_values.items():
        if artifact.get(key) != expected:
            findings.append(f"{case_id}: baseline isolation {key} must be {expected!r}")
    metadata_mentions = artifact.get("operatorPromptDddjangoSkillMetadataMentions")
    if metadata_mentions:
        findings.append(f"{case_id}: baseline isolation contains dddjango skill metadata mentions")
    return findings


def validate_baseline_output(raw_dir: Path, case_id: str, run_dir: Path) -> list[str]:
    path = raw_dir / f"{case_id}-baseline.txt"
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    findings: list[str] = []
    for label, pattern in BASELINE_CONTAMINATION_PATTERNS.items():
        if pattern.search(text):
            try:
                display_path = path.relative_to(run_dir)
            except ValueError:
                display_path = path
            findings.append(f"{display_path}: baseline output contains {label}")
    return findings


def validate_oracle(raw_dir: Path, case_id: str) -> list[str]:
    path = raw_dir / f"{case_id}-answer-oracle-evaluation.json"
    oracle, error = load_json_object(path)
    if error is not None:
        return [f"{case_id}: {error}"]
    assert oracle is not None
    schema_error = common.validate_oracle_schema(oracle, case_id)
    if schema_error is not None:
        return [f"{case_id}: invalid answer-oracle schema: {schema_error}"]
    return []


def workflow_trace_marker_exists(run_dir: Path) -> bool:
    return (run_dir / SUBAGENT_TRACE_MARKER).is_file()


def validate_workflow_trace_schema(
    *,
    run_dir: Path,
    raw_dir: Path,
    case_id: str,
    variant: str,
) -> list[str]:
    path = raw_dir / f"{case_id}-{variant}-subagent-trace.json"
    trace, error = load_json_object(path)
    if error is not None:
        return [f"{case_id} {variant}: missing workflow subagent trace artifact: {path}"]
    assert trace is not None

    findings: list[str] = []
    required_keys = {
        "caseId",
        "variant",
        "parserVersion",
        "sourceKind",
        "traceCaptureReliable",
        "responseSource",
        "eventSource",
        "spawnEventCount",
        "waitEventCount",
        "subagentToolEvents",
        "explicitActualClaims",
        "explicitFallbackClaims",
        "rolesMentioned",
        "traceStatus",
    }
    missing = sorted(required_keys - set(trace))
    if missing:
        findings.append(f"{path}: missing keys: {', '.join(missing)}")
        return findings
    if trace.get("caseId") != case_id:
        findings.append(f"{path}: caseId mismatch")
    if trace.get("variant") != variant:
        findings.append(f"{path}: variant mismatch")
    if not isinstance(trace.get("traceCaptureReliable"), bool):
        findings.append(f"{path}: traceCaptureReliable must be boolean")
    for key in ("spawnEventCount", "waitEventCount"):
        if not isinstance(trace.get(key), int):
            findings.append(f"{path}: {key} must be integer")
    for key in (
        "subagentToolEvents",
        "explicitActualClaims",
        "explicitFallbackClaims",
        "rolesMentioned",
    ):
        if not isinstance(trace.get(key), list):
            findings.append(f"{path}: {key} must be a list")

    for key in ("responseSource", "eventSource"):
        value = trace.get(key)
        if not isinstance(value, str):
            findings.append(f"{path}: {key} must be a string")
            continue
        _, path_error = safe_run_relative_path(run_dir, value)
        if path_error is not None:
            findings.append(f"{path}: {key}: {path_error}")

    reliable = trace.get("traceCaptureReliable") is True
    actual_claims = trace.get("explicitActualClaims")
    spawn_count = trace.get("spawnEventCount")
    wait_count = trace.get("waitEventCount")
    if (
        reliable
        and isinstance(actual_claims, list)
        and actual_claims
        and isinstance(spawn_count, int)
        and isinstance(wait_count, int)
        and spawn_count + wait_count == 0
    ):
        findings.append(f"{path}: actual subagent claim has no reliable spawn/wait trace")
    return findings


def validate_workflow_trace_artifacts(
    *,
    run_dir: Path,
    raw_dir: Path,
    case_id: str,
    variants: list[str],
) -> list[str]:
    if not workflow_trace_marker_exists(run_dir):
        return []
    findings: list[str] = []
    for variant in variants:
        findings.extend(
            validate_workflow_trace_schema(
                run_dir=run_dir,
                raw_dir=raw_dir,
                case_id=case_id,
                variant=variant,
            )
        )
    return findings


def load_code_capture_metadata() -> tuple[dict[str, Any], list[str]]:
    metadata, error = load_json_object(CODE_CAPTURE_METADATA)
    if error is not None:
        return {"cases": {}}, [error]
    assert metadata is not None
    cases = metadata.get("cases")
    if not isinstance(cases, dict):
        return metadata, [f"{CODE_CAPTURE_METADATA}: cases must be an object"]
    return metadata, []


def safe_run_relative_path(run_dir: Path, value: str) -> tuple[Path | None, str | None]:
    artifact_path = Path(value)
    if not value or artifact_path.is_absolute() or ".." in artifact_path.parts:
        return None, f"artifactPath must be run-relative and safe: {value}"
    resolved = (run_dir / artifact_path).resolve(strict=False)
    try:
        resolved.relative_to(run_dir.resolve())
    except ValueError:
        return None, f"artifactPath escapes run dir: {value}"
    return resolved, None


def validate_code_artifacts(
    *,
    run_dir: Path,
    case_id: str,
    variants: list[str],
    metadata: dict[str, Any],
) -> list[str]:
    cases = metadata.get("cases")
    if not isinstance(cases, dict):
        return []
    case_meta = cases.get(case_id)
    if not isinstance(case_meta, dict) or case_meta.get("captureCode") is not True:
        return []

    findings: list[str] = []
    for variant in variants:
        base = run_dir / "code" / case_id / variant
        manifest_path = base / "changed-files.json"
        diff_path = base / "diff.patch"
        if not require_file(findings, manifest_path, "code artifact manifest"):
            continue
        require_file(findings, diff_path, "code artifact diff")
        manifest, error = load_json_object(manifest_path)
        if error is not None:
            findings.append(error)
            continue
        assert manifest is not None

        required_manifest_keys = {
            "caseId",
            "variant",
            "evidenceMode",
            "diffPath",
            "noCodeProduced",
            "files",
        }
        missing = sorted(required_manifest_keys - set(manifest))
        if missing:
            findings.append(f"{manifest_path}: missing keys: {', '.join(missing)}")
            continue
        if manifest.get("caseId") != case_id:
            findings.append(f"{manifest_path}: caseId mismatch")
        if manifest.get("variant") != variant:
            findings.append(f"{manifest_path}: variant mismatch")
        if manifest.get("evidenceMode") != "code-backed":
            findings.append(f"{manifest_path}: evidenceMode must be code-backed")
        diff_value = manifest.get("diffPath")
        if not isinstance(diff_value, str):
            findings.append(f"{manifest_path}: diffPath must be a string")
        elif not diff_value:
            findings.append(f"{manifest_path}: diffPath must not be empty")
        else:
            _, path_error = safe_run_relative_path(run_dir, diff_value)
            if path_error is not None:
                findings.append(f"{manifest_path}: {path_error}")
        if not isinstance(manifest.get("noCodeProduced"), bool):
            findings.append(f"{manifest_path}: noCodeProduced must be a boolean")
        files = manifest.get("files")
        if not isinstance(files, list):
            findings.append(f"{manifest_path}: files must be a list")
            continue
        for entry in files:
            if not isinstance(entry, dict):
                findings.append(f"{manifest_path}: file entry must be an object")
                continue
            binary = entry.get("binary")
            if binary is not None and not isinstance(binary, bool):
                findings.append(f"{manifest_path}: binary must be boolean")
                continue
            if entry.get("binary") is True:
                continue
            artifact_raw = entry.get("artifactPath")
            if not isinstance(artifact_raw, str) or not artifact_raw:
                findings.append(f"{manifest_path}: artifactPath is required for non-binary file entries")
                continue
            artifact_value = artifact_raw
            artifact_file, path_error = safe_run_relative_path(run_dir, artifact_value)
            if path_error is not None:
                findings.append(f"{manifest_path}: {path_error}")
                continue
            assert artifact_file is not None
            if not artifact_file.is_file():
                entry_path = entry.get("path", artifact_value)
                findings.append(f"{manifest_path}: missing copied source file for {entry_path}: {artifact_file}")
    return findings


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        run_id = validate_run_id(args.run_id)
        bucket = common.bucket_paths(args.bucket)
        case_paths = common.selected_case_paths(args.bucket, args.case)
        variants = selected_variants(args.variant)
        run_dir = resolved_under(bucket.runs_dir, run_id, description="run path")
    except SystemExit as exc:
        if isinstance(exc.code, int):
            raise
        print(f"FAIL: {exc.code}")
        raise SystemExit(1) from exc
    raw_dir = run_dir / "raw"

    findings: list[str] = []
    if not run_dir.is_dir():
        findings.append(f"missing run directory: {run_dir}")
    if not raw_dir.is_dir():
        findings.append(f"missing raw artifact directory: {raw_dir}")

    code_metadata: dict[str, Any] = {"cases": {}}
    if args.bucket == "code":
        code_metadata, metadata_findings = load_code_capture_metadata()
        findings.extend(metadata_findings)

    for case_path in case_paths:
        case_id = case_path.stem
        if not case_path.is_file():
            findings.append(f"missing public case: {case_path}")
        findings.extend(validate_answer_yaml(bucket.answer_dir, case_id, args.bucket))
        findings.extend(
            validate_common_run_artifacts(
                run_dir=run_dir,
                raw_dir=raw_dir,
                case_id=case_id,
                variants=variants,
                allow_skipped_exits=args.allow_skipped_exits,
            )
        )
        if not args.skip_oracle:
            findings.extend(validate_oracle(raw_dir, case_id))
        if args.bucket == "code":
            findings.extend(
                validate_code_artifacts(
                    run_dir=run_dir,
                    case_id=case_id,
                    variants=variants,
                    metadata=code_metadata,
                )
            )
        if args.bucket == "workflow":
            findings.extend(
                validate_workflow_trace_artifacts(
                    run_dir=run_dir,
                    raw_dir=raw_dir,
                    case_id=case_id,
                    variants=variants,
                )
            )

    if findings:
        for finding in findings:
            print(f"FAIL: {finding}")
        raise SystemExit(1)

    print(
        f"PASS: validated {len(case_paths)} case(s), {len(variants)} variant(s) "
        f"for {args.bucket}/{run_id}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
