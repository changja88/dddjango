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
import eval_run_identity as run_identity
import validate_eval_code_artifacts as code_artifacts
import eval_leakage_policy
import workflow_execution_gate as workflow_gate


REPO_ROOT = common.REPO_ROOT
EVAL_ROOT = common.EVAL_ROOT
CODE_CAPTURE_METADATA = EVAL_ROOT / "code/cases/plugin/code-capture.json"
SUBAGENT_TRACE_MARKER = "SUBAGENT_TRACE_CAPTURE.json"

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
    run_identity.validate_production_run_id(run_id)
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


def require_json_prompt_input_file(findings: list[str], path: Path, description: str) -> bool:
    if not require_file(findings, path, description):
        return False
    try:
        raw_text = path.read_text(encoding="utf-8")
    except OSError as exc:
        findings.append(f"{description} is unreadable: {path}: {exc}")
        return False
    if not raw_text.strip():
        findings.append(f"{description} must contain a JSON object or array: {path}")
        return False
    try:
        value = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        findings.append(f"{description} must contain a JSON object or array: {path}: {exc}")
        return False
    if not isinstance(value, (dict, list)):
        findings.append(f"{description} must contain a JSON object or array: {path}")
        return False
    return True


def validate_prompt_input_private_material(raw_dir: Path, case_id: str) -> list[str]:
    path = raw_dir / f"{case_id}-with-dddjango-prompt-input.json"
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    private_keys = {
        "case_id",
        "reference_basis",
        "target_behavior",
        "scoring_checks",
        "failure_modes",
        "leakage_checks",
        "evidence_required",
        "coverage_tags",
    }
    private_markers = (
        "__DDDJANGO_PRIVATE_EVAL_SENTINEL__",
        "EVALUATOR-ONLY ANSWER ORACLE",
        "workspace/develop/eval/response/answer/",
        "workspace/develop/eval/code/answer/",
        "workspace/develop/eval/plugin/answer/",
        "workspace/develop/eval/runtime/answer/",
        "workspace/develop/eval/source/answer/",
        "workspace/develop/eval/workflow/answer/",
        "workspace/develop/eval/response/cases/plugin/private/",
        "workspace/develop/eval/code/cases/plugin/private/",
        "workspace/develop/eval/plugin/cases/plugin/private/",
        "workspace/develop/eval/runtime/cases/plugin/private/",
        "workspace/develop/eval/source/cases/plugin/private/",
        "workspace/develop/eval/workflow/cases/plugin/private/",
        "target_behavior:",
        "reference_basis:",
        "case_id:",
        "scoring_checks:",
        "failure_modes:",
        "leakage_checks:",
        "evidence_required:",
        "coverage_tags:",
    )
    if any(marker in text for marker in private_markers):
        return [
            f"with-ddjango prompt-input artifact contains private evaluation material: {path}"
        ]
    try:
        artifact = json.loads(text)
    except json.JSONDecodeError:
        return []
    if json_has_private_key(artifact, private_keys):
        return [
            f"with-ddjango prompt-input artifact contains private evaluation material: {path}"
        ]
    return []


def json_has_private_key(value: Any, private_keys: set[str]) -> bool:
    if isinstance(value, dict):
        if any(key in private_keys for key in value):
            return True
        return any(json_has_private_key(child, private_keys) for child in value.values())
    if isinstance(value, list):
        return any(json_has_private_key(child, private_keys) for child in value)
    return False


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
        require_json_prompt_input_file(
            findings,
            raw_dir / f"{case_id}-with-dddjango-prompt-input.json",
            "with-ddjango prompt-input artifact",
        )
        require_file(
            findings,
            raw_dir / f"{case_id}-with-dddjango-prompt-input.stderr.txt",
            "with-ddjango prompt-input stderr artifact",
        )
        findings.extend(validate_prompt_input_private_material(raw_dir, case_id))

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
    for marker in baseline_hidden_repo_path_markers():
        if marker in text:
            try:
                display_path = path.relative_to(run_dir)
            except ValueError:
                display_path = path
            findings.append(f"{display_path}: baseline output contains hidden repo path")
    return findings


def display_run_path(run_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(run_dir).as_posix()
    except ValueError:
        return path.as_posix()


def forbidden_local_path_markers() -> list[str]:
    return baseline_hidden_repo_path_markers()


def local_path_scan_artifacts(
    *,
    run_dir: Path,
    raw_dir: Path,
    case_id: str,
    variants: list[str],
) -> list[Path]:
    paths = [
        raw_dir / f"{case_id}-answer-oracle-evaluation.json",
        run_dir / "analysis/report.html",
    ]
    for variant in variants:
        paths.extend(
            [
                raw_dir / f"{case_id}-{variant}.txt",
                raw_dir / f"{case_id}-{variant}-events.jsonl",
                raw_dir / f"{case_id}-{variant}.stderr.txt",
                raw_dir / f"{case_id}-{variant}-prompt-input.json",
                raw_dir / f"{case_id}-{variant}-prompt-input.stderr.txt",
            ]
        )
    return [path for path in paths if path.is_file()]


def generic_leakage_scan_artifacts(
    *,
    run_dir: Path,
    raw_dir: Path,
    case_id: str,
    variants: list[str],
) -> list[Path]:
    paths = [
        raw_dir / f"{case_id}-answer-oracle-evaluation.json",
        run_dir / "analysis/report.html",
    ]
    for variant in variants:
        if variant == "baseline":
            continue
        paths.extend(
            [
                raw_dir / f"{case_id}-{variant}.txt",
                raw_dir / f"{case_id}-{variant}.stderr.txt",
            ]
        )
    return [path for path in paths if path.is_file()]


def validate_forbidden_local_paths(
    *,
    bucket: str,
    run_dir: Path,
    raw_dir: Path,
    case_id: str,
    variants: list[str],
) -> list[str]:
    markers = forbidden_local_path_markers()
    findings: list[str] = []
    paths = local_path_scan_artifacts(
        run_dir=run_dir,
        raw_dir=raw_dir,
        case_id=case_id,
        variants=variants,
    )
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        if any(marker in text for marker in markers):
            display_path = display_run_path(run_dir, path)
            findings.append(f"{display_path}: output contains forbidden local path")
    generic_paths = generic_leakage_scan_artifacts(
        run_dir=run_dir,
        raw_dir=raw_dir,
        case_id=case_id,
        variants=variants,
    )
    public_prompt_categories = public_prompt_leakage_categories(raw_dir, case_id)
    for leakage in eval_leakage_policy.scan_files_for_leakage(generic_paths):
        if (
            leakage.path == run_dir / "analysis/report.html"
            and leakage.category in public_prompt_categories
        ):
            continue
        if is_allowed_generic_leakage(
            bucket=bucket,
            raw_dir=raw_dir,
            case_id=case_id,
            variants=variants,
            path=leakage.path,
            category=leakage.category,
            public_prompt_categories=public_prompt_categories,
        ):
            continue
        display_path = display_run_path(run_dir, leakage.path)
        findings.append(f"{display_path}: output contains {leakage.category}")
    return findings


def public_prompt_leakage_categories(raw_dir: Path, case_id: str) -> set[str]:
    path = raw_dir / f"{case_id}-public-prompt.md"
    if not path.is_file():
        return set()
    text = path.read_text(encoding="utf-8", errors="replace")
    return set(eval_leakage_policy.scan_text_for_leakage(text))


def is_allowed_generic_leakage(
    *,
    bucket: str,
    raw_dir: Path,
    case_id: str,
    variants: list[str],
    path: Path,
    category: str,
    public_prompt_categories: set[str],
) -> bool:
    """Allow Codex file links in code answers without weakening report leakage checks."""
    allowed_response_paths = {
        raw_dir / f"{case_id}-{variant}.txt"
        for variant in variants
    }
    if path not in allowed_response_paths:
        return False
    if category in public_prompt_categories:
        return True
    return bucket == "code" and category == "temporary workspace path"


def baseline_forbidden_paths() -> list[Path]:
    paths = [
        Path("dddjango/skills"),
        Path("dddjango/.codex-plugin/plugin.json"),
        Path(".agents/plugins/marketplace.json"),
        Path(".codex/plugins/cache/dddjango-local"),
        Path("plugins/dddjango"),
        Path("plugins/cache/dddjango-local"),
        Path("workspace/develop/eval/source/crosswalks"),
    ]
    for bucket in common.BUCKETS:
        paths.append(Path("workspace/develop/eval") / bucket / "answer")
        paths.append(Path("workspace/develop/eval") / bucket / "runs")
        paths.append(Path("workspace/develop/eval") / bucket / "cases/plugin/private")
    return paths


def baseline_hidden_repo_path_markers() -> list[str]:
    markers: list[str] = []
    for rel_path in baseline_forbidden_paths():
        absolute = REPO_ROOT / rel_path
        markers.append(absolute.as_posix())
        resolved = absolute.resolve(strict=False).as_posix()
        if resolved != markers[-1]:
            markers.append(resolved)
    return sorted(set(markers))


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


def answer_section_scalar(text: str, section: str, key: str) -> str | None:
    lines = text.splitlines()
    in_section = False
    for line in lines:
        if not in_section:
            if re.match(rf"^{re.escape(section)}\s*:\s*$", line):
                in_section = True
            continue
        if line and not line.startswith(" "):
            break
        match = re.match(rf"^\s+{re.escape(key)}\s*:\s*(.*?)\s*(?:#.*)?$", line)
        if match:
            value = match.group(1).strip().strip("'\"")
            return value
    return None


def score_value(score: object) -> int | None:
    if not isinstance(score, str):
        return None
    match = re.match(r"^\s*(\d+)\s*/\s*5\s*$", score)
    if not match:
        return None
    return int(match.group(1))


def validate_expected_outcomes(
    *,
    answer_dir: Path,
    raw_dir: Path,
    case_id: str,
) -> list[str]:
    answer_path = answer_dir / f"{case_id}.yaml"
    answer_text = answer_path.read_text(encoding="utf-8", errors="replace")
    baseline_expected = answer_section_scalar(answer_text, "expected_outcomes", "baseline")
    with_expected = answer_section_scalar(answer_text, "expected_outcomes", "with_dddjango")
    expected_delta = answer_section_scalar(answer_text, "expected_outcomes", "expected_delta")
    baseline_pass_ok = answer_section_scalar(answer_text, "expected_outcomes", "baseline_pass_ok")
    if (
        baseline_expected is None
        and with_expected is None
        and expected_delta is None
        and baseline_pass_ok is None
    ):
        return []

    oracle, error = load_json_object(raw_dir / f"{case_id}-answer-oracle-evaluation.json")
    if error is not None:
        return []
    assert oracle is not None
    baseline = oracle.get("baseline")
    with_dddjango = oracle.get("with_dddjango")
    findings: list[str] = []
    baseline_verdict = baseline.get("verdict") if isinstance(baseline, dict) else None
    with_verdict = with_dddjango.get("verdict") if isinstance(with_dddjango, dict) else None
    if baseline_pass_ok == "false" and baseline_verdict == "pass":
        findings.append(
            f"{case_id}: expected_outcomes baseline_pass_ok=false conflicts with baseline verdict pass"
        )
    if baseline_expected in {"fail", "partial"} and baseline_verdict == "pass":
        findings.append(
            f"{case_id}: expected_outcomes baseline={baseline_expected} conflicts with baseline verdict pass"
        )
    if with_expected == "pass" and with_verdict != "pass":
        findings.append(
            f"{case_id}: expected_outcomes with_dddjango=pass conflicts with with-ddjango verdict {with_verdict}"
        )
    if (
        with_expected == "pass-or-pass-limited"
        and with_verdict not in {"pass", "pass-limited"}
    ):
        findings.append(
            f"{case_id}: expected_outcomes with_dddjango=pass-or-pass-limited conflicts with with-ddjango verdict {with_verdict}"
        )
    if expected_delta in {"positive", "non-negative"}:
        baseline_score = score_value(baseline.get("score") if isinstance(baseline, dict) else None)
        with_score = score_value(with_dddjango.get("score") if isinstance(with_dddjango, dict) else None)
        if (
            expected_delta == "non-negative"
            and baseline_score is not None
            and with_score is not None
            and with_score < baseline_score
        ):
            findings.append(
                f"{case_id}: expected_outcomes expected_delta=non-negative requires with-dddjango score at least baseline"
            )
    if expected_delta == "positive":
        if baseline_score is not None and with_score is not None and with_score <= baseline_score:
            findings.append(
                f"{case_id}: expected_outcomes expected_delta=positive requires with-dddjango score above baseline"
            )
        if with_verdict == baseline_verdict == "pass":
            findings.append(
                f"{case_id}: expected_outcomes expected_delta=positive conflicts with both variants passing"
            )
    return findings


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
    parser_version = trace.get("parserVersion")
    if isinstance(parser_version, int) and parser_version >= 2:
        required_keys.add("resultEventCount")
        required_keys.update(
            {
                "spawnedAgentIds",
                "collectedAgentIds",
                "uncollectedAgentIds",
            }
        )
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
    if "resultEventCount" in trace and not isinstance(trace.get("resultEventCount"), int):
        findings.append(f"{path}: resultEventCount must be integer")
    list_keys = [
        "subagentToolEvents",
        "explicitActualClaims",
        "explicitFallbackClaims",
        "rolesMentioned",
    ]
    if isinstance(parser_version, int) and parser_version >= 2:
        list_keys.extend(
            [
                "spawnedAgentIds",
                "collectedAgentIds",
                "uncollectedAgentIds",
            ]
        )
    for key in list_keys:
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


def variant_oracle_key(variant: str) -> str:
    return "with_dddjango" if variant == common.VARIANTS[1] else variant


def validate_workflow_execution_gate(
    *,
    answer_dir: Path,
    raw_dir: Path,
    case_id: str,
    variants: list[str],
) -> list[str]:
    answer_text = (answer_dir / f"{case_id}.yaml").read_text(
        encoding="utf-8",
        errors="replace",
    )
    oracle, error = load_json_object(raw_dir / f"{case_id}-answer-oracle-evaluation.json")
    if error is not None:
        return []
    assert oracle is not None

    findings: list[str] = []
    for variant in variants:
        trace, trace_error = load_json_object(
            raw_dir / f"{case_id}-{variant}-subagent-trace.json"
        )
        if trace_error is not None:
            trace = {"traceStatus": "missing trace"}
        assert trace is not None

        gate = workflow_gate.gate_findings(
            answer_text=answer_text,
            trace=trace,
            case_id=case_id,
            variant=variant,
        )
        key = variant_oracle_key(variant)
        variant_oracle = oracle.get(key)
        verdict = variant_oracle.get("verdict") if isinstance(variant_oracle, dict) else None
        if gate.findings and verdict not in {"fail", "blocked"}:
            findings.extend(gate.findings)
    return findings


def answer_has_workflow_execution_expectation(answer_dir: Path, case_id: str) -> bool:
    answer_path = answer_dir / f"{case_id}.yaml"
    if not answer_path.is_file():
        return False
    return workflow_gate.parse_workflow_expectation(
        answer_path.read_text(encoding="utf-8", errors="replace")
    ) is not None


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
    answer_dir: Path,
) -> list[str]:
    cases = metadata.get("cases")
    if not isinstance(cases, dict):
        return []
    case_meta = cases.get(case_id)
    if not isinstance(case_meta, dict) or case_meta.get("captureCode") is not True:
        return []

    findings: list[str] = []
    try:
        answer_text = code_artifacts.load_answer_oracle(answer_dir, case_id)
        code_expected = code_artifacts.answer_code_expected(answer_text, case_id)
        deterministic_checks = code_artifacts.parse_deterministic_checks(answer_text, case_id)
        behavior_checks = code_artifacts.parse_behavior_checks(answer_text, case_id)
    except AssertionError as exc:
        return [str(exc)]

    for variant in variants:
        try:
            code_artifacts.validate_manifest(
                run_dir,
                case_id,
                variant,
                answer_text=answer_text,
                code_expected=code_expected,
            )
            code_artifacts.validate_deterministic_check_artifacts(
                run_dir,
                case_id,
                variant,
                deterministic_checks,
            )
            code_artifacts.validate_behavior_check_artifacts(
                run_dir,
                case_id,
                variant,
                behavior_checks,
            )
            findings.extend(
                validate_code_verification_claims(
                    run_dir=run_dir,
                    case_id=case_id,
                    variant=variant,
                )
            )
        except AssertionError as exc:
            findings.append(str(exc))
    return findings


CLAIM_TOOL_PATTERNS = {
    "pytest": re.compile(r"\bpytest\b", re.I),
    "unittest": re.compile(r"\bunittest\b", re.I),
    "compileall": re.compile(r"\bcompileall\b|컴파일", re.I),
    "ruff": re.compile(r"\bruff\b", re.I),
    "mypy": re.compile(r"\bmypy\b", re.I),
    "pyright": re.compile(r"\bpyright\b", re.I),
}
PYTHON_UNITTEST_COMMAND_PATTERN = re.compile(r"\bpython3?\s+-m\s+unittest(?:\s+[A-Za-z0-9_./:-]+)*")
PRE_FAILURE_CLAIM_PATTERN = re.compile(
    r"(구현\s*전|먼저|before implementation|red[- ]green|failing test|실패하는 테스트|실패 확인|실패하는 것 확인)",
    re.I,
)
CLAIM_POSITIVE_PATTERN = re.compile(
    r"\b(pass(?:ed|es)?|ok|success(?:ful)?|green)\b|실행|통과|완료",
    re.I,
)
CLAIM_NEGATIVE_PATTERN = re.compile(
    r"\b(?:not run|not executed|did not run|was not run|unrun)\b|미실행|실행하지|하지 않았|안 했|안함|아님|아닌",
    re.I,
)
GENERIC_EXECUTION_CLAIM_PATTERNS = {
    "validator": re.compile(r"\bvalidator(?:s)?\b|\bvalidation\b|검증", re.I),
    "eval": re.compile(r"\beval(?:uator|uation|s)?\b", re.I),
    "browser": re.compile(r"\bbrowser\b|브라우저", re.I),
    "Serena": re.compile(r"\bserena\b", re.I),
}
GENERIC_EXECUTION_EVIDENCE_PATTERNS = {
    "validator": re.compile(r"validate_|validator|pytest|unittest|ruff|mypy|pyright|test_validate", re.I),
    "eval": re.compile(r"run_eval|evaluate_eval|eval_run|eval_bucket|answer-oracle-evaluation", re.I),
    "browser": re.compile(r"browser_|playwright|screenshot", re.I),
    "Serena": re.compile(r"serena", re.I),
}


def code_check_commands(run_dir: Path, case_id: str, variant: str) -> list[str]:
    artifact_dir = run_dir / "code" / case_id / variant
    commands: list[str] = []
    for path in sorted(artifact_dir.rglob("*-command.txt")):
        try:
            commands.append(path.read_text(encoding="utf-8", errors="replace").lower())
        except OSError:
            continue
    return commands


def code_check_has_failing_exit(run_dir: Path, case_id: str, variant: str) -> bool:
    artifact_dir = run_dir / "code" / case_id / variant
    for path in sorted(artifact_dir.rglob("*-exit.txt")):
        try:
            exit_code = path.read_text(encoding="utf-8", errors="replace").strip()
        except OSError:
            continue
        if exit_code and exit_code != "0":
            return True
    return False


def normalized_command(value: str) -> str:
    return " ".join(value.strip().split()).lower()


def line_claims_tool_execution(line: str, tool: str, pattern: re.Pattern[str]) -> bool:
    if not pattern.search(line):
        return False
    lowered = line.lower()
    if CLAIM_NEGATIVE_PATTERN.search(lowered):
        return False
    if CLAIM_POSITIVE_PATTERN.search(lowered):
        return True
    return tool in {"pytest", "ruff", "mypy", "pyright"} and any(
        word in lowered for word in ("test", "check", "검증", "테스트")
    )


def validate_code_verification_claims(
    *,
    run_dir: Path,
    case_id: str,
    variant: str,
) -> list[str]:
    output_path = run_dir / "raw" / f"{case_id}-{variant}.txt"
    try:
        output = output_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    commands = code_check_commands(run_dir, case_id, variant)
    normalized_commands = [normalized_command(command) for command in commands]
    has_failing_exit = code_check_has_failing_exit(run_dir, case_id, variant)
    findings: list[str] = []
    for line_number, line in enumerate(output.splitlines(), start=1):
        lowered = line.lower()
        if (
            PRE_FAILURE_CLAIM_PATTERN.search(line)
            and not CLAIM_NEGATIVE_PATTERN.search(lowered)
            and not has_failing_exit
        ):
            findings.append(
                f"{case_id} {variant}: output claims pre-implementation failing/red-green verification without separate failing check artifact at raw/{case_id}-{variant}.txt:{line_number}"
            )
        for match in PYTHON_UNITTEST_COMMAND_PATTERN.finditer(line):
            if CLAIM_NEGATIVE_PATTERN.search(lowered):
                continue
            claimed_command = normalized_command(match.group(0))
            if claimed_command not in normalized_commands:
                findings.append(
                    f"{case_id} {variant}: output claims command `{claimed_command}` without exact matching check command artifact at raw/{case_id}-{variant}.txt:{line_number}"
                )
        for tool, pattern in CLAIM_TOOL_PATTERNS.items():
            if not line_claims_tool_execution(line, tool, pattern):
                continue
            if any(tool in command for command in commands):
                continue
            findings.append(
                f"{case_id} {variant}: output claims {tool} execution without matching check command artifact at raw/{case_id}-{variant}.txt:{line_number}"
            )
    return findings


def line_claims_generic_execution(line: str, pattern: re.Pattern[str]) -> bool:
    if not pattern.search(line):
        return False
    lowered = line.lower()
    if CLAIM_NEGATIVE_PATTERN.search(lowered):
        return False
    if any(
        marker in lowered
        for marker in (
            "not-run",
            "not run",
            "not executed",
            "not used",
            "skipped",
            "unavailable",
            "missing",
            "blocked",
            "미실행",
            "실행하지",
            "사용하지",
            "못했",
            "못했다",
            "못 한",
            "못한",
            "볼 수 없",
        )
    ):
        return False
    if any(
        marker in lowered
        for marker in (
            "gate",
            "claim",
            "detector",
            "evidence",
            "responsibility",
            "criteria",
            "required",
            "requires",
            "needed",
            "필요",
            "기준",
            "책임",
            "증거",
            "요구",
            "검토",
            "인정",
            "허위",
            "읽고",
            "생략",
            "reference",
            "routing",
            "red-green-refactor",
            "result as evidence",
            "결과",
            "전용",
        )
    ):
        return False
    return bool(CLAIM_POSITIVE_PATTERN.search(lowered))


def event_item_execution_text(item: Any) -> str:
    if not isinstance(item, dict):
        return ""
    item_type = item.get("type")
    values: list[str] = []
    if item_type == "command_execution":
        command = item.get("command")
        if isinstance(command, str):
            values.append(command)
    tool = item.get("tool")
    if isinstance(tool, str):
        values.append(tool)
    return "\n".join(values)


def variant_event_evidence(raw_dir: Path, case_id: str, variant: str) -> str:
    path = raw_dir / f"{case_id}-{variant}-events.jsonl"
    if not path.is_file():
        return ""
    evidence: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        item = event.get("item")
        evidence_text = event_item_execution_text(item)
        if evidence_text:
            evidence.append(evidence_text)
    return "\n".join(evidence)


def validate_generic_execution_claims(
    *,
    raw_dir: Path,
    case_id: str,
    variants: list[str],
) -> list[str]:
    findings: list[str] = []
    for variant in variants:
        output_path = raw_dir / f"{case_id}-{variant}.txt"
        if not output_path.is_file():
            continue
        output = output_path.read_text(encoding="utf-8", errors="replace")
        event_text = variant_event_evidence(raw_dir, case_id, variant)
        for line_number, line in enumerate(output.splitlines(), start=1):
            for label, claim_pattern in GENERIC_EXECUTION_CLAIM_PATTERNS.items():
                if not line_claims_generic_execution(line, claim_pattern):
                    continue
                evidence_pattern = GENERIC_EXECUTION_EVIDENCE_PATTERNS[label]
                if evidence_pattern.search(event_text):
                    continue
                findings.append(
                    f"{case_id} {variant}: output claims {label} execution without matching event evidence at raw/{case_id}-{variant}.txt:{line_number}"
                )
    return findings


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        run_id = validate_run_id(args.run_id)
        identity = run_identity.parse_run_id(run_id)
        if identity.bucket != args.bucket:
            raise SystemExit(
                f"run id bucket mismatch: run id bucket={identity.bucket}, --bucket={args.bucket}"
            )
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
    run_meta_errors = run_identity.validate_run_meta(run_dir)
    if run_meta_errors:
        raise SystemExit("\n".join(run_meta_errors))

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
        findings.extend(
            validate_forbidden_local_paths(
                bucket=args.bucket,
                run_dir=run_dir,
                raw_dir=raw_dir,
                case_id=case_id,
                variants=variants,
            )
        )
        findings.extend(
            validate_generic_execution_claims(
                raw_dir=raw_dir,
                case_id=case_id,
                variants=variants,
            )
        )
        if not args.skip_oracle:
            findings.extend(validate_oracle(raw_dir, case_id))
            findings.extend(
                validate_expected_outcomes(
                    answer_dir=bucket.answer_dir,
                    raw_dir=raw_dir,
                    case_id=case_id,
                )
            )
        if args.bucket == "code":
            findings.extend(
                validate_code_artifacts(
                    run_dir=run_dir,
                    case_id=case_id,
                    variants=variants,
                    metadata=code_metadata,
                    answer_dir=bucket.answer_dir,
                )
            )
        has_workflow_expectation = answer_has_workflow_execution_expectation(
            bucket.answer_dir,
            case_id,
        )
        if args.bucket == "workflow" or has_workflow_expectation:
            findings.extend(
                validate_workflow_trace_artifacts(
                    run_dir=run_dir,
                    raw_dir=raw_dir,
                    case_id=case_id,
                    variants=variants,
                )
            )
            if has_workflow_expectation and not args.skip_oracle:
                findings.extend(
                    validate_workflow_execution_gate(
                        answer_dir=bucket.answer_dir,
                        raw_dir=raw_dir,
                        case_id=case_id,
                        variants=variants,
                    )
                )

    if findings:
        run_identity.write_run_validation_manifest(
            run_dir,
            run_id=run_id,
            bucket=args.bucket,
            case_ids=[case_path.stem for case_path in case_paths],
            variants=variants,
            status="failed",
            findings=findings,
        )
        for finding in findings:
            print(f"FAIL: {finding}")
        raise SystemExit(1)

    run_identity.write_run_validation_manifest(
        run_dir,
        run_id=run_id,
        bucket=args.bucket,
        case_ids=[case_path.stem for case_path in case_paths],
        variants=variants,
        status="passed",
        findings=[],
    )
    print(
        f"PASS: validated {len(case_paths)} case(s), {len(variants)} variant(s) "
        f"for {args.bucket}/{run_id}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
