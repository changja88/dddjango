#!/usr/bin/env python3
"""Validate dddjango eval bucket case/answer packs.

This is a structural and contamination validator for buckets that do not yet
have a full model-run harness. It intentionally does not score model quality.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import workflow_execution_gate as workflow_gate
import eval_answer_yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
EVAL_ROOT = REPO_ROOT / "workspace/develop/eval"
BUCKETS = ("response", "code", "plugin", "runtime", "source", "workflow")
REQUIRED_FIELDS = (
    "id",
    "case_id",
    "bucket",
    "kind",
    "public_case",
    "intent",
    "reference_basis",
    "target_behavior",
    "scoring_checks",
    "hard_gates",
    "failure_modes",
    "leakage_checks",
    "evidence_required",
    "control_case",
    "expected_outcomes",
    "coverage_tags",
)
ANSWER_ONLY_PUBLIC_PATTERNS = {
    "answer field: reference_basis": re.compile(r"(?<![A-Za-z0-9_])reference_basis(?![A-Za-z0-9_])"),
    "answer field: target_behavior": re.compile(r"(?<![A-Za-z0-9_])target_behavior(?![A-Za-z0-9_])"),
    "answer field: scoring_checks": re.compile(r"(?<![A-Za-z0-9_])scoring_checks(?![A-Za-z0-9_])"),
    "answer field: failure_modes": re.compile(r"(?<![A-Za-z0-9_])failure_modes(?![A-Za-z0-9_])"),
    "answer field: leakage_checks": re.compile(r"(?<![A-Za-z0-9_])leakage_checks(?![A-Za-z0-9_])"),
    "answer field: evidence_required": re.compile(r"(?<![A-Za-z0-9_])evidence_required(?![A-Za-z0-9_])"),
    "answer field: coverage_tags": re.compile(r"(?<![A-Za-z0-9_])coverage_tags(?![A-Za-z0-9_])"),
    "answer field: case_id": re.compile(r"\bcase_id\s*:"),
    "answer oracle wording": re.compile(r"\banswer oracle\b", re.I),
    "Korean private answer wording": re.compile(r"비공개\s*정답|정답\s*파일"),
    "absolute repo path": re.compile(re.escape(str(REPO_ROOT))),
}
LOCAL_HOME_DIRS = ("Users", "home")
ABSOLUTE_LOCAL_PATH = re.compile(
    r"(?m)^\s*(?:-\s*)?path\s*:\s*/(?:" + "|".join(LOCAL_HOME_DIRS) + r")/"
)
LIST_FIELDS = (
    "scoring_checks",
    "hard_gates",
    "failure_modes",
    "leakage_checks",
    "evidence_required",
    "coverage_tags",
)
CONTROL_CASE_VALUES = {
    "false",
    "restraint",
    "negative",
    "honesty",
    "safety",
}
EXPECTED_OUTCOME_FIELDS = (
    "baseline",
    "with_dddjango",
    "expected_delta",
    "baseline_pass_ok",
)
WORKFLOW_EXPECTATION_REQUIRED_FIELDS = (
    "expected_mode",
    "acceptable_modes",
    "forbidden_modes",
    "decision_rule",
    "responsibility_rule",
    "report_label",
)
REQUIRED_COVERAGE_TAGS = {
    "response": {
        "specialist-positive",
        "mixed-boundary",
        "ambiguity",
        "prompt-injection",
        "eval-leakage",
        "simple-negative",
        "false-claim",
        "validation-honesty",
    },
    "code": {
        "ddd-to-code",
        "django-implementation",
        "django-ninja-api",
        "db-consistency",
        "tdd",
        "test-implementation",
        "python-typing",
        "django-web",
        "negative-implementation-restraint",
        "no-code",
        "clarification",
        "command-honesty",
    },
    "plugin": {
        "trigger-quality",
        "routing-boundary",
        "progressive-disclosure",
        "runtime-reference-split",
        "provisional-handling",
        "agents-metadata",
        "packaging",
        "marketplace-sync",
        "leaked-answer-text",
        "cache-source-consistency",
        "runtime-safety",
    },
    "runtime": {
        "prompt-input-exposure",
        "baseline-isolation",
        "stale-cache",
        "missing-skill-metadata",
        "wrong-routing",
        "private-material-request",
        "answer-leakage-sentinel",
        "role-map-sync",
    },
    "source": {
        "docs-coherence",
        "source-provenance",
        "conflict-gap-decision",
        "provisional-handling",
        "drf-guardrail",
        "validation-coverage",
        "eval-traceability",
        "boundary-protection",
    },
    "workflow": {
        "positive-composite",
        "review-focused",
        "handoff-contract",
        "risky-write-consistency",
        "role-map-sync",
        "delegation-honesty",
        "sequential-fallback",
        "subagent-opt-out",
        "tiny-task-restraint",
        "false-claim",
        "integration-closure",
    },
}
MANUAL_PROTOCOL_BUCKETS = {"plugin", "runtime", "source", "workflow"}
MANUAL_PROTOCOL_REQUIRED_TERMS = (
    "cases/plugin/public",
    "answer/",
    "fixtures/",
    "runs/<run-id>/analysis/",
    "leakage",
    "evidence",
)
CODE_CASE_ROLE_VALUES = {"ddd_direct", "implementation_supporting", "control"}
DDD_OBSERVATION_FIELDS = (
    "business_problem",
    "subdomain_type",
    "subdomain_type_basis",
    "bounded_context",
    "context_map_or_not_applicable",
    "ubiquitous_terms",
    "aggregate_root",
    "aggregate_behavior",
    "invariants",
    "application_service_boundary",
    "transaction_boundary",
    "django_mapping",
    "test_evidence",
)
DDD_REQUIRED_REFERENCE_PATHS = {
    "workspace/reference/architecture-ddd/reference/final.md",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--bucket",
        action="append",
        choices=BUCKETS,
        help="Bucket to validate. Repeatable. Defaults to all buckets.",
    )
    return parser.parse_args()


def scalar_value(text: str, key: str) -> str | None:
    match = re.search(rf"(?m)^\s*{re.escape(key)}\s*:\s*(.+?)\s*$", text)
    if not match:
        return None
    return match.group(1).strip().strip("'\"")


def has_field(text: str, key: str) -> bool:
    return bool(re.search(rf"(?m)^\s*{re.escape(key)}\s*:", text))


def block_lines(text: str, key: str) -> list[str]:
    lines = text.splitlines()
    start: int | None = None
    for index, line in enumerate(lines):
        if re.match(rf"^\s*{re.escape(key)}\s*:", line):
            start = index + 1
            break
    if start is None:
        return []
    result: list[str] = []
    for line in lines[start:]:
        if line and not line.startswith(" "):
            break
        if line.strip():
            result.append(line)
    return result


def validate_reference_basis(path: Path, text: str) -> list[str]:
    findings: list[str] = []
    lines = block_lines(text, "reference_basis")
    path_count = sum(1 for line in lines if re.match(r"^\s*-\s+path\s*:", line))
    basis_count = sum(1 for line in lines if re.match(r"^\s+basis\s*:", line))
    if path_count == 0:
        findings.append(f"{path}: reference_basis must contain structured '- path:' entries")
    if path_count != basis_count:
        findings.append(f"{path}: reference_basis path/basis count mismatch")
    if ABSOLUTE_LOCAL_PATH.search("\n".join(lines)):
        findings.append(f"{path}: reference_basis contains local absolute /Users path")
    return findings


def yaml_list_values(text: str, key: str) -> list[str]:
    values: list[str] = []
    for line in block_lines(text, key):
        match = re.match(r"^\s*-\s+(.+?)\s*$", line)
        if not match:
            continue
        value = match.group(1).strip().strip("'\"")
        if value:
            values.append(value)
    return values


def validate_required_blocks(path: Path, text: str) -> list[str]:
    findings: list[str] = []
    for field in LIST_FIELDS:
        if has_field(text, field) and not yaml_list_values(text, field):
            findings.append(f"{path}: {field} must contain at least one list item")
    if has_field(text, "target_behavior") and not block_lines(text, "target_behavior"):
        findings.append(f"{path}: target_behavior must not be empty")
    return findings


def validate_expected_outcomes(path: Path, text: str) -> list[str]:
    findings: list[str] = []
    if not has_field(text, "expected_outcomes"):
        return findings
    block = "\n".join(block_lines(text, "expected_outcomes"))
    for field in EXPECTED_OUTCOME_FIELDS:
        if not re.search(rf"(?m)^\s+{re.escape(field)}\s*:", block):
            findings.append(f"{path}: expected_outcomes missing {field}")
    return findings


def validate_control_case(path: Path, text: str) -> list[str]:
    value = scalar_value(text, "control_case")
    if value is None:
        return []
    if value.lower() in CONTROL_CASE_VALUES:
        return []
    return [
        f"{path}: control_case must be one of {', '.join(sorted(CONTROL_CASE_VALUES))}"
    ]


def validate_workflow_execution_expectation(path: Path, text: str) -> list[str]:
    findings: list[str] = []
    if not has_field(text, "workflow_execution_expectation"):
        return [f"{path}: missing workflow_execution_expectation"]
    block = "\n".join(block_lines(text, "workflow_execution_expectation"))
    expectation = workflow_gate.parse_workflow_expectation(text)
    for field in WORKFLOW_EXPECTATION_REQUIRED_FIELDS:
        if not re.search(rf"(?m)^\s*{re.escape(field)}\s*:", block):
            findings.append(
                f"{path}: workflow_execution_expectation missing {field}"
            )
    mode_values = {
        "acceptable_modes": expectation.acceptable_modes if expectation else (),
        "forbidden_modes": expectation.forbidden_modes if expectation else (),
    }
    for field, values in mode_values.items():
        if not values:
            findings.append(
                f"{path}: workflow_execution_expectation {field} must contain at least one list item"
            )
    acceptable = set(mode_values["acceptable_modes"])
    forbidden = set(mode_values["forbidden_modes"])
    overlap = sorted(acceptable & forbidden)
    if overlap:
        findings.append(
            f"{path}: workflow_execution_expectation acceptable_modes and forbidden_modes overlap: {', '.join(overlap)}"
        )
    unknown = sorted(
        mode for mode in acceptable | forbidden if mode not in workflow_gate.KNOWN_MODES
    )
    if unknown:
        findings.append(
            f"{path}: workflow_execution_expectation contains unknown machine mode(s): {', '.join(unknown)}"
        )
    return findings


def validate_runtime_metadata_answer(path: Path, text: str) -> list[str]:
    if "missing-skill-metadata" not in set(yaml_list_values(text, "coverage_tags")):
        return []
    findings: list[str] = []
    evidence = [value.lower() for value in yaml_list_values(text, "evidence_required")]
    if not any("validation command output" in value for value in evidence):
        findings.append(
            f"{path}: missing-skill-metadata answer must require validation command output"
        )
    text_lower = text.lower()
    if "semantic metadata alignment" not in text_lower and "semantically align" not in text_lower:
        findings.append(
            f"{path}: missing-skill-metadata answer must require semantic metadata alignment"
        )
    return findings


def validate_code_ddd_answer(path: Path, text: str) -> list[str]:
    role = eval_answer_yaml.scalar_value(text, "case_role")
    findings: list[str] = []
    if role not in CODE_CASE_ROLE_VALUES:
        findings.append(
            f"{path}: code answer case_role must be one of {', '.join(sorted(CODE_CASE_ROLE_VALUES))}"
        )
        return findings
    if role != "ddd_direct":
        return []

    reference_paths = {
        item.get("path", "")
        for item in eval_answer_yaml.list_of_maps(text, "reference_basis")
    }
    for required_path in sorted(DDD_REQUIRED_REFERENCE_PATHS - reference_paths):
        findings.append(f"{path}: ddd_direct answer must reference {required_path}")

    observation_keys = eval_answer_yaml.nested_keys(text, "ddd_observations")
    if not observation_keys:
        findings.append(f"{path}: DDD code answer must declare ddd_observations")
        return findings
    for field in DDD_OBSERVATION_FIELDS:
        if field not in observation_keys:
            findings.append(f"{path}: ddd_observations missing {field}")
    return findings


def validate_answer(path: Path, bucket: str, public_case: Path) -> list[str]:
    findings: list[str] = []
    text = path.read_text(encoding="utf-8")
    case_id = path.stem
    for field in REQUIRED_FIELDS:
        if not has_field(text, field):
            findings.append(f"{path}: missing {field}")
    expected_public = public_case.relative_to(REPO_ROOT).as_posix()
    expected = {
        "id": case_id,
        "case_id": case_id,
        "bucket": bucket,
        "kind": bucket,
        "public_case": expected_public,
    }
    for key, value in expected.items():
        actual = scalar_value(text, key)
        if actual != value:
            findings.append(f"{path}: {key} mismatch, expected {value!r}, got {actual!r}")
    findings.extend(validate_reference_basis(path, text))
    findings.extend(validate_required_blocks(path, text))
    findings.extend(validate_expected_outcomes(path, text))
    findings.extend(validate_control_case(path, text))
    if bucket == "workflow":
        findings.extend(validate_workflow_execution_expectation(path, text))
    if bucket == "runtime":
        findings.extend(validate_runtime_metadata_answer(path, text))
    if bucket == "code":
        code_expected = scalar_value(text, "code_expected")
        if code_expected not in {"true", "false"}:
            findings.append(f"{path}: code answer must declare code_expected: true|false")
        if code_expected == "false" and not scalar_value(text, "code_expected_reason"):
            findings.append(f"{path}: code_expected false requires code_expected_reason")
        findings.extend(validate_code_ddd_answer(path, text))
    return findings


def validate_coverage(bucket: str, answers: list[Path]) -> list[str]:
    required = REQUIRED_COVERAGE_TAGS[bucket]
    observed: set[str] = set()
    for answer in answers:
        observed.update(yaml_list_values(answer.read_text(encoding="utf-8"), "coverage_tags"))
    missing = sorted(required - observed)
    if not missing:
        return []
    return [f"{bucket}: coverage_tags missing required eval_goal coverage: {', '.join(missing)}"]


def validate_manual_protocol(bucket: str) -> list[str]:
    if bucket not in MANUAL_PROTOCOL_BUCKETS:
        return []
    path = EVAL_ROOT / bucket / "manual_protocol.md"
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return [f"{bucket}: missing manual protocol: {path}"]
    text_lower = text.lower()
    missing = [term for term in MANUAL_PROTOCOL_REQUIRED_TERMS if term.lower() not in text_lower]
    if missing:
        return [f"{path}: missing manual protocol term(s): {', '.join(missing)}"]
    return []


def validate_public_case(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    findings = [
        f"{path}: public case leaks {label}"
        for label, pattern in ANSWER_ONLY_PUBLIC_PATTERNS.items()
        if pattern.search(text)
    ]
    if path.stem == "case-code-web-detail":
        text_lower = text.lower()
        has_blank_memo = (
            "blank memo" in text_lower
            or "empty memo" in text_lower
            or "빈 memo" in text_lower
            or "빈 메모" in text_lower
            or ("memo" in text_lower and "빈 문자열" in text_lower)
            or ("메모" in text_lower and "빈 문자열" in text_lower)
        )
        has_fallback = "fallback" in text_lower or "대체" in text_lower or "placeholder" in text_lower
        if not (has_blank_memo and has_fallback):
            findings.append(f"{path}: case-code-web-detail public case must mention blank memo fallback")
        has_detail_css = "detail.css" in text_lower
        has_reference = (
            "reference" in text_lower
            or "referenced" in text_lower
            or "참조" in text_lower
            or "연결" in text_lower
        )
        if not (has_detail_css and has_reference):
            findings.append(f"{path}: case-code-web-detail public case must mention detail.css reference")
    return findings


def validate_code_capture(public_case_ids: set[str]) -> list[str]:
    metadata_path = EVAL_ROOT / "code/cases/plugin/code-capture.json"
    findings: list[str] = []
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [f"missing code capture metadata: {metadata_path}"]
    except json.JSONDecodeError as exc:
        return [f"invalid code capture metadata: {metadata_path}: {exc}"]
    cases = metadata.get("cases")
    if not isinstance(cases, dict):
        return [f"{metadata_path}: cases must be an object"]
    metadata_ids = set(cases)
    if metadata_ids != public_case_ids:
        findings.append(
            f"{metadata_path}: public/metadata case mismatch "
            f"public={sorted(public_case_ids - metadata_ids)} metadata={sorted(metadata_ids - public_case_ids)}"
        )
    for case_id, config in cases.items():
        if not isinstance(config, dict):
            findings.append(f"{metadata_path}: {case_id} metadata must be an object")
            continue
        if config.get("captureCode") is not True:
            findings.append(f"{metadata_path}: {case_id} captureCode must be true")
        subject_repo = config.get("subjectRepo")
        if not isinstance(subject_repo, str) or not subject_repo:
            findings.append(f"{metadata_path}: {case_id} subjectRepo is required")
            continue
        if not (REPO_ROOT / subject_repo).is_dir():
            findings.append(f"{metadata_path}: {case_id} subjectRepo does not exist: {subject_repo}")
    return findings


def validate_bucket(bucket: str) -> tuple[int, list[str]]:
    base = EVAL_ROOT / bucket
    public_dir = base / "cases/plugin/public"
    answer_dir = base / "answer"
    public_cases = sorted(path for path in public_dir.glob("case-*.md") if path.name != ".gitkeep")
    answers = sorted(answer_dir.glob("case-*.yaml"))
    findings: list[str] = []
    public_ids = {path.stem for path in public_cases}
    answer_ids = {path.stem for path in answers}
    if not public_cases:
        findings.append(f"{bucket}: no public cases")
    if public_ids != answer_ids:
        findings.append(
            f"{bucket}: public/answer mismatch public={sorted(public_ids - answer_ids)} "
            f"answer={sorted(answer_ids - public_ids)}"
        )
    for public_case in public_cases:
        findings.extend(validate_public_case(public_case))
        answer_path = answer_dir / f"{public_case.stem}.yaml"
        if answer_path.is_file():
            findings.extend(validate_answer(answer_path, bucket, public_case))
    findings.extend(validate_coverage(bucket, answers))
    findings.extend(validate_manual_protocol(bucket))
    if bucket == "code":
        findings.extend(validate_code_capture(public_ids))
    return len(public_cases), findings


def main() -> int:
    args = parse_args()
    buckets = args.bucket or list(BUCKETS)
    all_findings: list[str] = []
    counts: dict[str, int] = {}
    for bucket in buckets:
        count, findings = validate_bucket(bucket)
        counts[bucket] = count
        all_findings.extend(findings)
    if all_findings:
        for finding in all_findings:
            print(f"FAIL: {finding}")
        return 1
    print("eval bucket pack validation passed: " + ", ".join(f"{k}={v}" for k, v in counts.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
