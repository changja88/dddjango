#!/usr/bin/env python3
"""Validate code-backed eval artifacts for captured source changes."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
METADATA_PATH = REPO_ROOT / "workspace/develop/eval/code/cases/plugin/code-capture.json"
ANSWER_DIR = REPO_ROOT / "workspace/develop/eval/code/answer"
VALID_VARIANTS = ("baseline", "with-dddjango")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, default=METADATA_PATH)
    parser.add_argument("--answer-dir", type=Path, default=ANSWER_DIR)
    parser.add_argument("--case", action="append", dest="cases", required=True)
    parser.add_argument("--variant", action="append", choices=VALID_VARIANTS, required=True)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise AssertionError(f"missing metadata file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise AssertionError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise AssertionError(f"{path} must contain a JSON object")
    return value


def load_answer_oracle(answer_dir: Path, case_id: str) -> str:
    path = answer_dir / f"{case_id}.yaml"
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise AssertionError(f"missing answer oracle: {path}") from exc
    if not text.strip():
        raise AssertionError(f"empty answer oracle: {path}")
    case_pattern = re.compile(
        rf"(?m)^\s*case_id\s*:\s*['\"]?{re.escape(case_id)}['\"]?\s*(?:#.*)?$"
    )
    kind_pattern = re.compile(r"(?m)^\s*kind\s*:\s*['\"]?code['\"]?\s*(?:#.*)?$")
    if not case_pattern.search(text):
        raise AssertionError(f"{path}: missing matching case_id: {case_id}")
    if not kind_pattern.search(text):
        raise AssertionError(f"{path}: missing kind: code")
    return text


def answer_code_expected(answer_text: str, case_id: str) -> bool:
    match = re.search(r"(?m)^\s*code_expected\s*:\s*(true|false)\s*(?:#.*)?$", answer_text, re.I)
    if not match:
        raise AssertionError(f"{case_id}: answer oracle must declare code_expected: true|false")
    code_expected = match.group(1).lower() == "true"
    if not code_expected:
        reason = re.search(r"(?m)^\s*code_expected_reason\s*:\s*([^#\n]+?)\s*(?:#.*)?$", answer_text)
        if not reason or not reason.group(1).strip().strip("'\""):
            raise AssertionError(f"{case_id}: code_expected: false requires code_expected_reason")
    return code_expected


def run_relative_path(run_dir: Path, value: str) -> Path:
    artifact_path = Path(value)
    if artifact_path.is_absolute() or ".." in artifact_path.parts:
        raise AssertionError(f"artifactPath must be run-relative and safe: {value}")
    resolved = (run_dir / artifact_path).resolve()
    try:
        resolved.relative_to(run_dir.resolve())
    except ValueError as exc:
        raise AssertionError(f"artifactPath escapes run dir: {value}") from exc
    return resolved


def validate_baseline_isolation(run_dir: Path, case_id: str) -> None:
    path = run_dir / "raw" / f"{case_id}-baseline-isolation.json"
    artifact = load_json(path)
    if artifact.get("pass") is not True:
        raise AssertionError(f"{case_id}: baseline isolation artifact pass=false")


def validate_manifest(run_dir: Path, case_id: str, variant: str, *, allow_no_code: bool) -> None:
    base = run_dir / "code" / case_id / variant
    manifest_path = base / "changed-files.json"
    diff_path = base / "diff.patch"
    if not manifest_path.is_file():
        raise AssertionError(f"missing code artifact manifest: {manifest_path}")
    if not diff_path.is_file():
        raise AssertionError(f"missing code artifact diff: {diff_path}")

    manifest = load_json(manifest_path)
    required_manifest_keys = {
        "caseId",
        "variant",
        "workspace",
        "evidenceMode",
        "diffPath",
        "noCodeProduced",
        "files",
    }
    missing = sorted(required_manifest_keys - set(manifest))
    if missing:
        raise AssertionError(f"{manifest_path} missing keys: {', '.join(missing)}")
    if manifest["caseId"] != case_id:
        raise AssertionError(f"{manifest_path} caseId mismatch")
    if manifest["variant"] != variant:
        raise AssertionError(f"{manifest_path} variant mismatch")
    if manifest["evidenceMode"] != "code-backed":
        raise AssertionError(f"{manifest_path} evidenceMode must be code-backed")

    files = manifest["files"]
    if not isinstance(files, list):
        raise AssertionError(f"{manifest_path} files must be a list")
    if manifest["noCodeProduced"]:
        if not allow_no_code:
            raise AssertionError(f"{manifest_path} noCodeProduced=true is not allowed for this case")
        return
    if not files:
        raise AssertionError(f"{manifest_path} must list at least one changed source file")

    required_file_keys = {
        "path",
        "status",
        "language",
        "artifactPath",
        "lineCount",
        "byteCount",
        "binary",
    }
    copied_text_files = 0
    for entry in files:
        if not isinstance(entry, dict):
            raise AssertionError(f"{manifest_path} file entry must be an object")
        missing = sorted(required_file_keys - set(entry))
        if missing:
            raise AssertionError(f"{manifest_path} file entry missing keys: {', '.join(missing)}")
        if not isinstance(entry["binary"], bool):
            raise AssertionError(f"{manifest_path} binary must be boolean")
        artifact_file = run_relative_path(run_dir, str(entry["artifactPath"]))
        if not entry["binary"]:
            if not artifact_file.is_file():
                raise AssertionError(f"missing copied source file: {artifact_file}")
            copied_text_files += 1
    if copied_text_files == 0:
        raise AssertionError(f"{manifest_path} must include at least one copied text source file")


def main() -> int:
    args = parse_args()
    run_dir = args.run_dir
    if not run_dir.is_absolute():
        run_dir = REPO_ROOT / run_dir
    answer_dir = args.answer_dir if args.answer_dir.is_absolute() else REPO_ROOT / args.answer_dir
    metadata = load_json(args.metadata)
    cases = metadata.get("cases")
    if not isinstance(cases, dict):
        raise AssertionError("metadata must contain a cases object")

    checked = 0
    skipped = 0
    for case_id in args.cases:
        case_meta = cases.get(case_id, {})
        if not isinstance(case_meta, dict):
            raise AssertionError(f"case metadata must be an object: {case_id}")
        if not case_meta.get("captureCode"):
            raise AssertionError(f"{case_id}: captureCode must be true for code artifact validation")
        answer_text = load_answer_oracle(answer_dir, case_id)
        allow_no_code = answer_code_expected(answer_text, case_id) is False
        if "baseline" in args.variant:
            validate_baseline_isolation(run_dir, case_id)
        for variant in args.variant:
            validate_manifest(run_dir, case_id, variant, allow_no_code=allow_no_code)
            checked += 1
    if checked == 0:
        raise AssertionError("no code artifacts were checked")
    print(f"code artifact validation passed: {checked} checked, {skipped} response-only skipped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
