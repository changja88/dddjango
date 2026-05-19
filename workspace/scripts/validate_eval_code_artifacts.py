#!/usr/bin/env python3
"""Validate code-backed eval artifacts for captured source changes."""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
from pathlib import Path
from typing import Any

try:
    import eval_answer_yaml
except ModuleNotFoundError:
    from workspace.scripts import eval_answer_yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
METADATA_PATH = REPO_ROOT / "workspace/develop/eval/code/cases/plugin/code-capture.json"
ANSWER_DIR = REPO_ROOT / "workspace/develop/eval/code/answer"
GENERATED_ARTIFACT_PATTERNS = (
    "*.sqlite3",
    "db.sqlite3",
    "**/__pycache__/**",
    "*.pyc",
    ".pytest_cache/**",
)
POLICY_FINDINGS_FILENAME = "policy-findings.json"
VALID_VARIANTS = ("baseline", "with-dddjango")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, default=METADATA_PATH)
    parser.add_argument("--answer-dir", type=Path, default=ANSWER_DIR)
    parser.add_argument("--case", action="append", dest="cases", required=True)
    parser.add_argument("--variant", action="append", choices=VALID_VARIANTS, required=True)
    return parser.parse_args(argv)


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


def yaml_scalar(value: str) -> str:
    value = value.strip()
    if " #" in value:
        value = value.split(" #", 1)[0].rstrip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def parse_key_value(text: str) -> tuple[str, str]:
    if ":" not in text:
        raise ValueError(text)
    key, value = text.split(":", 1)
    return key.strip(), yaml_scalar(value)


def parse_deterministic_checks(answer_text: str, case_id: str) -> list[dict[str, object]]:
    lines = answer_text.splitlines()
    start_index: int | None = None
    inline_value = ""
    for index, line in enumerate(lines):
        match = re.match(r"^deterministic_checks\s*:\s*(.*)$", line)
        if match:
            start_index = index
            inline_value = match.group(1).strip()
            break
    if start_index is None:
        raise AssertionError(f"{case_id}: answer oracle must declare deterministic_checks")
    if inline_value == "[]":
        return []
    if inline_value:
        raise AssertionError(f"{case_id}: deterministic_checks must be a YAML list or []")

    checks: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    for line in lines[start_index + 1 :]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if re.match(r"^[^\s].*:\s*", line):
            break
        if line.startswith("  - "):
            if current is not None:
                checks.append(current)
            current = {}
            rest = line[4:].strip()
            if rest:
                try:
                    key, value = parse_key_value(rest)
                except ValueError as exc:
                    raise AssertionError(
                        f"{case_id}: invalid deterministic check item: {rest}"
                    ) from exc
                current[key] = value
            continue
        if line.startswith("    ") and current is not None:
            stripped = line.strip()
            try:
                key, value = parse_key_value(stripped)
            except ValueError as exc:
                raise AssertionError(
                    f"{case_id}: invalid deterministic check field: {stripped}"
                ) from exc
            current[key] = value
            continue
        raise AssertionError(f"{case_id}: invalid deterministic_checks indentation: {line}")
    if current is not None:
        checks.append(current)

    for check in checks:
        validate_deterministic_check_config(case_id, check)
    return checks


def parse_behavior_checks(answer_text: str, case_id: str) -> list[dict[str, object]]:
    lines = answer_text.splitlines()
    start_index: int | None = None
    inline_value = ""
    for index, line in enumerate(lines):
        match = re.match(r"^behavior_checks\s*:\s*(.*)$", line)
        if match:
            start_index = index
            inline_value = match.group(1).strip()
            break
    if start_index is None or inline_value == "[]":
        return []
    if inline_value:
        raise AssertionError(f"{case_id}: behavior_checks must be a YAML list or []")

    checks: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    for line in lines[start_index + 1 :]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if re.match(r"^[^\s].*:\s*", line):
            break
        if line.startswith("  - "):
            if current is not None:
                checks.append(current)
            current = {}
            rest = line[4:].strip()
            if rest:
                try:
                    key, value = parse_key_value(rest)
                except ValueError as exc:
                    raise AssertionError(
                        f"{case_id}: invalid behavior check item: {rest}"
                    ) from exc
                current[key] = value
            continue
        if line.startswith("    ") and current is not None:
            stripped = line.strip()
            try:
                key, value = parse_key_value(stripped)
            except ValueError as exc:
                raise AssertionError(
                    f"{case_id}: invalid behavior check field: {stripped}"
                ) from exc
            current[key] = value
            continue
        raise AssertionError(f"{case_id}: invalid behavior_checks indentation: {line}")
    if current is not None:
        checks.append(current)

    for check in checks:
        validate_behavior_check_config(case_id, check)
    return checks


def validate_deterministic_check_config(case_id: str, check: dict[str, object]) -> None:
    required = {"id", "command", "expected_exit", "evidence"}
    missing = sorted(required - set(check))
    if missing:
        raise AssertionError(
            f"{case_id}: deterministic check missing keys: {', '.join(missing)}"
        )
    check_id = check["id"]
    if not isinstance(check_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", check_id):
        raise AssertionError(f"{case_id}: invalid deterministic check id: {check_id}")
    command = check["command"]
    if not isinstance(command, str) or not command.strip():
        raise AssertionError(f"{case_id}: deterministic check {check_id} command is required")
    try:
        check["expected_exit"] = int(str(check["expected_exit"]).strip())
    except ValueError as exc:
        raise AssertionError(
            f"{case_id}: deterministic check {check_id} expected_exit must be an integer"
        ) from exc
    if check["evidence"] != "command-artifact":
        raise AssertionError(
            f"{case_id}: deterministic check {check_id} evidence must be command-artifact"
        )


def validate_behavior_check_config(case_id: str, check: dict[str, object]) -> None:
    required = {"id", "command", "expected_exit"}
    missing = sorted(required - set(check))
    if missing:
        raise AssertionError(
            f"{case_id}: behavior check missing keys: {', '.join(missing)}"
        )
    check_id = check["id"]
    if not isinstance(check_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", check_id):
        raise AssertionError(f"{case_id}: invalid behavior check id: {check_id}")
    command = check["command"]
    if not isinstance(command, str) or not command.strip():
        raise AssertionError(f"{case_id}: behavior check {check_id} command is required")
    try:
        check["expected_exit"] = int(str(check["expected_exit"]).strip())
    except ValueError as exc:
        raise AssertionError(
            f"{case_id}: behavior check {check_id} expected_exit must be an integer"
        ) from exc


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


def path_matches(pattern: str, changed_path: str) -> bool:
    return fnmatch.fnmatchcase(changed_path, pattern)


def write_policy_findings(
    run_dir: Path,
    case_id: str,
    variant: str,
    findings: list[dict[str, object]],
) -> None:
    path = run_dir / "code" / case_id / variant / POLICY_FINDINGS_FILENAME
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "caseId": case_id,
        "variant": variant,
        "findings": findings,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_policy_findings(run_dir: Path, case_id: str, variant: str) -> list[dict[str, object]]:
    path = run_dir / "code" / case_id / variant / POLICY_FINDINGS_FILENAME
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    if not isinstance(payload, dict):
        return []
    findings = payload.get("findings")
    if not isinstance(findings, list):
        return []
    return [finding for finding in findings if isinstance(finding, dict)]


def append_policy_findings(
    run_dir: Path,
    case_id: str,
    variant: str,
    findings: list[dict[str, object]],
) -> None:
    if not findings:
        return
    write_policy_findings(
        run_dir,
        case_id,
        variant,
        [*load_policy_findings(run_dir, case_id, variant), *findings],
    )


def quality_path_findings(answer_text: str, changed_paths: list[str]) -> list[dict[str, object]]:
    allowed_paths = eval_answer_yaml.list_values(answer_text, "allowed_paths")
    forbidden_paths = eval_answer_yaml.list_values(answer_text, "forbidden_paths")
    findings: list[dict[str, object]] = []
    for changed_path in changed_paths:
        if any(path_matches(pattern, changed_path) for pattern in forbidden_paths):
            continue
        if any(path_matches(pattern, changed_path) for pattern in GENERATED_ARTIFACT_PATTERNS):
            continue
        if allowed_paths and not any(path_matches(pattern, changed_path) for pattern in allowed_paths):
            findings.append(
                {
                    "severity": "quality",
                    "rule": "allowed_paths",
                    "path": changed_path,
                    "message": f"changed path is outside scoring allowed_paths: {changed_path}",
                    "allowedPaths": allowed_paths,
                }
            )
    return findings


def validate_manifest(
    run_dir: Path,
    case_id: str,
    variant: str,
    *,
    answer_text: str,
    code_expected: bool,
) -> None:
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
        if code_expected:
            raise AssertionError(f"{manifest_path} noCodeProduced=true is not allowed for this case")
        if files:
            raise AssertionError(f"{manifest_path} noCodeProduced=true requires empty files")
        write_policy_findings(run_dir, case_id, variant, [])
        return
    if not code_expected:
        raise AssertionError(f"{manifest_path} code_expected=false forbids code changes")
    if not files:
        raise AssertionError(f"{manifest_path} must list at least one changed source file")

    forbidden_paths = eval_answer_yaml.list_values(answer_text, "forbidden_paths")
    changed_paths = [
        str(entry.get("path") or "")
        for entry in files
        if isinstance(entry, dict)
    ]
    for changed_path in changed_paths:
        if any(path_matches(pattern, changed_path) for pattern in forbidden_paths):
            raise AssertionError(f"{case_id} {variant} forbidden path changed: {changed_path}")
        if any(path_matches(pattern, changed_path) for pattern in GENERATED_ARTIFACT_PATTERNS):
            raise AssertionError(f"{case_id} {variant} generated artifact changed: {changed_path}")
    quality_findings = quality_path_findings(answer_text, changed_paths)

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
    write_policy_findings(run_dir, case_id, variant, quality_findings)


def validate_deterministic_check_artifacts(
    run_dir: Path,
    case_id: str,
    variant: str,
    checks: list[dict[str, object]],
) -> None:
    for check in checks:
        check_id = str(check["id"])
        base = run_dir / "code" / case_id / variant / "checks"
        paths = {
            "command": base / f"{check_id}-command.txt",
            "exit": base / f"{check_id}-exit.txt",
            "stdout": base / f"{check_id}-stdout.txt",
            "stderr": base / f"{check_id}-stderr.txt",
        }
        if not all(path.is_file() for path in paths.values()):
            raise AssertionError(
                f"{case_id} {variant} missing deterministic check evidence: {check_id}"
            )
        actual_exit = paths["exit"].read_text(encoding="utf-8", errors="replace").strip()
        expected_exit = str(check["expected_exit"])
        if actual_exit != expected_exit:
            raise AssertionError(
                f"{case_id} {variant} deterministic check {check_id} exit must be "
                f"{expected_exit}: {actual_exit}"
            )


def validate_behavior_check_artifacts(
    run_dir: Path,
    case_id: str,
    variant: str,
    checks: list[dict[str, object]],
) -> None:
    quality_findings: list[dict[str, object]] = []
    for check in checks:
        check_id = str(check["id"])
        base = run_dir / "code" / case_id / variant / "behavior-checks"
        paths = {
            "command": base / f"{check_id}-command.txt",
            "exit": base / f"{check_id}-exit.txt",
            "stdout": base / f"{check_id}-stdout.txt",
            "stderr": base / f"{check_id}-stderr.txt",
        }
        if not all(path.is_file() for path in paths.values()):
            raise AssertionError(
                f"{case_id} {variant} missing behavior check evidence: {check_id}"
            )
        actual_exit = paths["exit"].read_text(encoding="utf-8", errors="replace").strip()
        expected_exit = str(check["expected_exit"])
        if actual_exit != expected_exit:
            finding = {
                "severity": "quality",
                "rule": "behavior_check_exit",
                "checkId": check_id,
                "expectedExit": expected_exit,
                "actualExit": actual_exit,
                "message": (
                    f"behavior check {check_id} exit was {actual_exit}, "
                    f"expected {expected_exit}"
                ),
            }
            quality_findings.append(finding)
            if variant == "with-dddjango":
                append_policy_findings(run_dir, case_id, variant, quality_findings)
                raise AssertionError(
                    f"{case_id} {variant} behavior check {check_id} exit must be "
                    f"{expected_exit}: {actual_exit}"
                )
    append_policy_findings(run_dir, case_id, variant, quality_findings)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
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
        code_expected = answer_code_expected(answer_text, case_id)
        deterministic_checks = parse_deterministic_checks(answer_text, case_id)
        behavior_checks = parse_behavior_checks(answer_text, case_id)
        if "baseline" in args.variant:
            validate_baseline_isolation(run_dir, case_id)
        for variant in args.variant:
            validate_manifest(
                run_dir,
                case_id,
                variant,
                answer_text=answer_text,
                code_expected=code_expected,
            )
            validate_deterministic_check_artifacts(
                run_dir,
                case_id,
                variant,
                deterministic_checks,
            )
            validate_behavior_check_artifacts(
                run_dir,
                case_id,
                variant,
                behavior_checks,
            )
            checked += 1
    if checked == 0:
        raise AssertionError("no code artifacts were checked")
    print(f"code artifact validation passed: {checked} checked, {skipped} response-only skipped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
