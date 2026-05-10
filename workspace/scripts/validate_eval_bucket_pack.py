#!/usr/bin/env python3
"""Validate dddjango eval bucket case/answer packs.

This is a structural and contamination validator for buckets that do not yet
have a full model-run harness. It intentionally does not score model quality.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


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
    "failure_modes",
    "leakage_checks",
    "evidence_required",
    "coverage_tags",
)
ANSWER_ONLY_PUBLIC_PATTERNS = {
    "answer field: target_behavior": re.compile(r"\btarget_behavior\b"),
    "answer field: scoring_checks": re.compile(r"\bscoring_checks\b"),
    "answer field: failure_modes": re.compile(r"\bfailure_modes\b"),
    "answer field: evidence_required": re.compile(r"\bevidence_required\b"),
    "answer field: case_id": re.compile(r"\bcase_id\s*:"),
    "answer oracle wording": re.compile(r"\banswer oracle\b", re.I),
    "absolute repo path": re.compile(re.escape(str(REPO_ROOT))),
}
ABSOLUTE_LOCAL_PATH = re.compile(r"(?m)^\s*(?:-\s*)?path\s*:\s*/Users/")


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
    if bucket == "code":
        code_expected = scalar_value(text, "code_expected")
        if code_expected not in {"true", "false"}:
            findings.append(f"{path}: code answer must declare code_expected: true|false")
        if code_expected == "false" and not scalar_value(text, "code_expected_reason"):
            findings.append(f"{path}: code_expected false requires code_expected_reason")
    return findings


def validate_public_case(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    findings = [
        f"{path}: public case leaks {label}"
        for label, pattern in ANSWER_ONLY_PUBLIC_PATTERNS.items()
        if pattern.search(text)
    ]
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
