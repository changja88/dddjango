#!/usr/bin/env python3
"""Fixture-first eval skeleton for the dddjango rebuild plan.

The script intentionally uses only the Python standard library. P4 validates
the evaluator mechanics before any model-backed skill cases are added.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VARIANTS = ("baseline", "with-plugin")
PASS_STATUSES = {"pass"}
FAIL_STATUSES = {"partial", "fail", "not-scored"}
LEAK_MARKERS: tuple[tuple[str, str], ...] = (
    ("local-path", "__FORBIDDEN_LOCAL_PATH_SENTINEL__"),
    ("private-field", "__PRIVATE_FIELD_SENTINEL__"),
)


class EvalError(Exception):
    """Raised for command contract errors."""


@dataclass(frozen=True)
class Paths:
    fixture_root: Path
    output_dir: Path


def read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def load_cases(fixture_root: Path) -> list[dict[str, Any]]:
    cases = read_json(fixture_root / "cases.json")
    if not isinstance(cases, list):
        raise EvalError("cases.json must contain a list")
    return cases


def case_by_id(fixture_root: Path, case_id: str) -> dict[str, Any]:
    for case in load_cases(fixture_root):
        if case.get("id") == case_id:
            return case
    raise EvalError(f"case not found: {case_id}")


def answer_path(fixture_root: Path, case_id: str, variant: str) -> Path:
    return fixture_root / "answers" / f"{case_id}.{variant}.json"


def oracle_path(fixture_root: Path, case_id: str, variant: str) -> Path:
    return fixture_root / "oracles" / f"{case_id}.{variant}.json"


def load_answer(fixture_root: Path, case_id: str, variant: str) -> tuple[dict[str, Any] | None, str | None]:
    path = answer_path(fixture_root, case_id, variant)
    if not path.is_file():
        return None, "missing-answer"
    try:
        answer = read_json(path)
    except json.JSONDecodeError:
        return None, "malformed-answer"
    if not isinstance(answer, dict):
        return None, "malformed-answer"
    return answer, None


def load_oracle(fixture_root: Path, case_id: str, variant: str) -> tuple[dict[str, Any] | None, str | None]:
    path = oracle_path(fixture_root, case_id, variant)
    if not path.is_file():
        return None, "missing-oracle"
    try:
        oracle = read_json(path)
    except json.JSONDecodeError:
        return None, "malformed-oracle"
    if not isinstance(oracle, dict):
        return None, "malformed-oracle"
    return oracle, None


def expected_outcome_conflict(case: dict[str, Any]) -> str | None:
    seen: dict[str, Any] = {}
    for outcome in case.get("expected_outcomes", []):
        if not isinstance(outcome, dict):
            return "expected-outcomes-malformed"
        key = outcome.get("id")
        value = outcome.get("value")
        if not key:
            return "expected-outcomes-malformed"
        if key in seen and seen[key] != value:
            return "expected-outcomes-conflict"
        seen[key] = value
    return None


def scan_markers(texts: list[str]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    joined = "\n".join(text for text in texts if text)
    for leak_class, marker in LEAK_MARKERS:
        count = joined.count(marker)
        if count:
            findings.append(
                {
                    "class": leak_class,
                    "count": count,
                    "marker_hash": sha256_text(marker),
                }
            )
    return findings


def command_observed(answer: dict[str, Any], expected_command: str) -> bool:
    for event in answer.get("structured_events", []):
        if not isinstance(event, dict):
            continue
        if event.get("type") not in {"command", "tool"}:
            continue
        if event.get("command") == expected_command or event.get("tool") == expected_command:
            return True
    return False


def score_variant(
    *,
    fixture_root: Path,
    case: dict[str, Any],
    variant: str,
) -> dict[str, Any]:
    case_id = str(case["id"])
    result: dict[str, Any] = {
        "case_id": case_id,
        "variant": variant,
        "status": "not-scored",
        "score": None,
        "failure_semantics": [],
        "checks": {},
    }

    conflict = expected_outcome_conflict(case)
    if conflict:
        result["failure_semantics"].append(conflict)
        return result

    answer, answer_error = load_answer(fixture_root, case_id, variant)
    if answer_error:
        result["failure_semantics"].append(answer_error)
        return result

    oracle, oracle_error = load_oracle(fixture_root, case_id, variant)
    if oracle_error:
        result["failure_semantics"].append(oracle_error)
        return result

    assert answer is not None
    assert oracle is not None
    expected_schema = oracle.get("schema_version")
    if expected_schema != "eval-oracle/v1":
        result["failure_semantics"].append("malformed-oracle")
        return result

    required_claims = oracle.get("required_claims", [])
    if not isinstance(required_claims, list):
        result["failure_semantics"].append("malformed-oracle")
        return result

    answer_claims = set(answer.get("claims", []))
    matched_claims = [claim for claim in required_claims if claim in answer_claims]
    claim_total = len(required_claims)
    claim_score = len(matched_claims) / claim_total if claim_total else 1.0
    result["checks"]["claims"] = {
        "required": required_claims,
        "matched": matched_claims,
        "score": claim_score,
    }

    expected_loaded_skill = oracle.get("loaded_skill")
    if expected_loaded_skill is not None:
        actual_loaded_skill = answer.get("loaded_skill")
        loaded_skill_ok = actual_loaded_skill == expected_loaded_skill
        result["checks"]["loaded_skill"] = {
            "expected": expected_loaded_skill,
            "actual": actual_loaded_skill,
            "ok": loaded_skill_ok,
        }
        if not loaded_skill_ok:
            result["failure_semantics"].append("wrong-routing")

    expected_command = oracle.get("required_command")
    if expected_command:
        command_ok = command_observed(answer, str(expected_command))
        result["checks"]["required_command"] = {
            "expected": expected_command,
            "observed_in_structured_event": command_ok,
        }
        if not command_ok:
            result["failure_semantics"].append("missing-structured-command-evidence")

    pre_texts = [str(answer.get("pre_redaction_text", "")), str(answer.get("stdout", "")), str(answer.get("stderr", ""))]
    persisted_texts = [str(answer.get("answer_text", ""))]
    pre_findings = scan_markers(pre_texts)
    persisted_findings = scan_markers(persisted_texts)
    result["checks"]["leakage"] = {
        "pre_redaction_findings": pre_findings,
        "persisted_artifact_findings": persisted_findings,
    }
    if pre_findings:
        result["failure_semantics"].append("raw-leakage")
    if persisted_findings:
        result["failure_semantics"].append("persisted-leakage")

    injected_failures = case.get("injected_failures", [])
    if "stale-report" in injected_failures:
        result["failure_semantics"].append("stale-report")

    if result["failure_semantics"]:
        result["score"] = claim_score
        result["status"] = "partial" if 0 < claim_score < 1 else "fail"
        return result

    result["score"] = claim_score
    if claim_score == 1.0:
        result["status"] = "pass"
    elif claim_score == 0:
        result["status"] = "fail"
        result["failure_semantics"].append("oracle-mismatch")
    else:
        result["status"] = "partial"
        result["failure_semantics"].append("oracle-partial")
    return result


def expected_fixture_status(case: dict[str, Any], variant: str) -> str:
    expected = case.get("fixture_expected", {})
    value = expected.get(variant)
    if value not in {"pass", "partial", "fail", "not-scored"}:
        raise EvalError(f"fixture_expected for {case['id']} {variant} is invalid: {value}")
    return str(value)


def run_one(paths: Paths, case_id: str, variant: str) -> dict[str, Any]:
    if variant not in VARIANTS:
        raise EvalError(f"variant must be one of {', '.join(VARIANTS)}")
    case = case_by_id(paths.fixture_root, case_id)
    result = score_variant(fixture_root=paths.fixture_root, case=case, variant=variant)
    result["expected_fixture_status"] = expected_fixture_status(case, variant)
    result["fixture_match"] = result["status"] == result["expected_fixture_status"]
    write_json(paths.output_dir / "raw" / "one.json", result)
    return result


def run_bucket(paths: Paths, bucket: str, run_id: str) -> dict[str, Any]:
    cases = [case for case in load_cases(paths.fixture_root) if case.get("bucket") == bucket]
    if not cases:
        raise EvalError(f"bucket not found or empty: {bucket}")

    results: list[dict[str, Any]] = []
    for case in cases:
        for variant in VARIANTS:
            result = score_variant(fixture_root=paths.fixture_root, case=case, variant=variant)
            result["expected_fixture_status"] = expected_fixture_status(case, variant)
            result["fixture_match"] = result["status"] == result["expected_fixture_status"]
            results.append(result)

    status_counts: dict[str, int] = {"pass": 0, "partial": 0, "fail": 0, "not-scored": 0}
    for result in results:
        status_counts[result["status"]] += 1

    hard_failures = [result for result in results if result["status"] in FAIL_STATUSES]
    fixture_mismatches = [result for result in results if not result["fixture_match"]]
    raw = {
        "schema_version": "eval-run/v1",
        "run_id": run_id,
        "bucket": bucket,
        "fixture_root": paths.fixture_root.as_posix(),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "variants": list(VARIANTS),
        "runtime_routing_evidence": "deferred-by-ADR-0004",
        "status": "fail" if hard_failures else "pass",
        "status_counts": status_counts,
        "hard_failure_count": len(hard_failures),
        "fixture_mismatch_count": len(fixture_mismatches),
        "results": results,
    }
    raw_digest = sha256_text(canonical_json(raw))
    raw["raw_digest"] = raw_digest
    write_json(paths.output_dir / "raw" / "run.json", raw)
    return raw


def render_report(output_dir: Path) -> dict[str, Any]:
    raw_path = output_dir / "raw" / "run.json"
    if not raw_path.is_file():
        raise EvalError(f"missing raw run artifact: {raw_path}")
    raw = read_json(raw_path)
    source_digest = sha256_text(canonical_json({key: value for key, value in raw.items() if key != "raw_digest"}))
    rows = []
    report_results: list[dict[str, Any]] = []
    for result in raw["results"]:
        case_id = result["case_id"]
        variant = result["variant"]
        status = result["status"]
        expected = result["expected_fixture_status"]
        semantics = ", ".join(result["failure_semantics"]) or "-"
        rows.append(
            "<tr>"
            f"<td>{html.escape(case_id)}</td>"
            f"<td>{html.escape(variant)}</td>"
            f"<td>{html.escape(status)}</td>"
            f"<td>{html.escape(expected)}</td>"
            f"<td>{html.escape(semantics)}</td>"
            "</tr>"
        )
        report_results.append(
            {
                "case_id": case_id,
                "variant": variant,
                "status": status,
                "expected_fixture_status": expected,
                "failure_semantics": result["failure_semantics"],
            }
        )

    report_json = {
        "schema_version": "eval-report/v1",
        "run_id": raw["run_id"],
        "source_raw_path": raw_path.as_posix(),
        "source_raw_digest": source_digest,
        "status_counts": raw["status_counts"],
        "runtime_routing_evidence": raw["runtime_routing_evidence"],
        "results": report_results,
    }
    write_json(output_dir / "report" / "report.json", report_json)
    html_text = "\n".join(
        [
            "<!doctype html>",
            "<html><head><meta charset=\"utf-8\"><title>dddjango P4 mini-bucket report</title></head>",
            "<body>",
            f"<h1>{html.escape(raw['run_id'])}</h1>",
            f"<p>Runtime routing evidence: {html.escape(raw['runtime_routing_evidence'])}</p>",
            f"<p>Raw digest: {html.escape(source_digest)}</p>",
            "<table>",
            "<thead><tr><th>case</th><th>variant</th><th>status</th><th>expected</th><th>failure semantics</th></tr></thead>",
            "<tbody>",
            *rows,
            "</tbody></table>",
            "</body></html>",
        ]
    )
    report_html = output_dir / "report" / "report.html"
    report_html.parent.mkdir(parents=True, exist_ok=True)
    report_html.write_text(html_text, encoding="utf-8")
    report_json["report_html_digest"] = sha256_file(report_html)
    write_json(output_dir / "report" / "report.json", report_json)
    return report_json


def validate_run(output_dir: Path) -> dict[str, Any]:
    raw_path = output_dir / "raw" / "run.json"
    report_path = output_dir / "report" / "report.json"
    failures: list[dict[str, Any]] = []
    if not raw_path.is_file():
        failures.append({"kind": "missing-raw-artifact", "path": raw_path.as_posix()})
    if not report_path.is_file():
        failures.append({"kind": "missing-report-artifact", "path": report_path.as_posix()})
    if failures:
        result = {"schema_version": "eval-validation/v1", "status": "fail", "failures": failures}
        write_json(output_dir / "validation" / "validate-run.json", result)
        return result

    raw = read_json(raw_path)
    report = read_json(report_path)
    raw_digest = sha256_text(canonical_json({key: value for key, value in raw.items() if key != "raw_digest"}))
    if raw.get("raw_digest") != raw_digest:
        failures.append({"kind": "raw-digest-mismatch"})
    if report.get("source_raw_digest") != raw_digest:
        failures.append({"kind": "stale-report", "expected": raw_digest, "actual": report.get("source_raw_digest")})
    if report.get("status_counts") != raw.get("status_counts"):
        failures.append({"kind": "report-status-count-mismatch"})

    raw_result_keys = {
        (item["case_id"], item["variant"]): (
            item["status"],
            item["expected_fixture_status"],
            tuple(item["failure_semantics"]),
        )
        for item in raw.get("results", [])
    }
    report_result_keys = {
        (item["case_id"], item["variant"]): (
            item["status"],
            item["expected_fixture_status"],
            tuple(item["failure_semantics"]),
        )
        for item in report.get("results", [])
    }
    if raw_result_keys != report_result_keys:
        failures.append({"kind": "report-raw-result-mismatch"})

    not_scored = [key for key, value in raw_result_keys.items() if value[0] == "not-scored"]
    if not_scored:
        failures.append({"kind": "not-scored-present", "count": len(not_scored)})

    fixture_mismatches = [item for item in raw.get("results", []) if not item.get("fixture_match")]
    if fixture_mismatches:
        failures.append({"kind": "fixture-status-mismatch", "count": len(fixture_mismatches)})

    expected_failure_semantics = {
        "missing-oracle",
        "malformed-oracle",
        "stale-report",
        "raw-leakage",
        "persisted-leakage",
        "expected-outcomes-conflict",
        "missing-structured-command-evidence",
    }
    observed_failure_semantics = {
        item
        for result in raw.get("results", [])
        for item in result.get("failure_semantics", [])
    }
    missing_semantics = sorted(expected_failure_semantics - observed_failure_semantics)
    if missing_semantics:
        failures.append({"kind": "missing-fixture-failure-semantics", "items": missing_semantics})

    result = {
        "schema_version": "eval-validation/v1",
        "status": "fail" if failures else "pass",
        "raw_path": raw_path.as_posix(),
        "report_path": report_path.as_posix(),
        "raw_digest": raw_digest,
        "status_counts": raw.get("status_counts"),
        "fixture_mismatch_count": len(fixture_mismatches),
        "observed_failure_semantics": sorted(observed_failure_semantics),
        "failures": failures,
    }
    write_json(output_dir / "validation" / "validate-run.json", result)
    return result


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture-root", default="workspace/develop/eval/fixtures/mini-bucket")
    parser.add_argument("--output-dir", default="workspace/develop/eval/runs/p4-mini-bucket-fixture")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_one_parser = subparsers.add_parser("run-one")
    run_one_parser.add_argument("--case-id", required=True)
    run_one_parser.add_argument("--variant", choices=VARIANTS, required=True)

    run_bucket_parser = subparsers.add_parser("run-bucket")
    run_bucket_parser.add_argument("--bucket", default="mini-bucket")
    run_bucket_parser.add_argument("--run-id", default="p4-mini-bucket-fixture")

    subparsers.add_parser("render-report")
    subparsers.add_parser("validate-run")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    paths = Paths(fixture_root=Path(args.fixture_root), output_dir=Path(args.output_dir))
    try:
        if args.command == "run-one":
            result = run_one(paths, args.case_id, args.variant)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result["status"] in PASS_STATUSES else 1
        if args.command == "run-bucket":
            raw = run_bucket(paths, args.bucket, args.run_id)
            print(json.dumps({"status": raw["status"], "status_counts": raw["status_counts"]}, ensure_ascii=False))
            return 0 if raw["status"] == "pass" else 1
        if args.command == "render-report":
            report = render_report(paths.output_dir)
            print(json.dumps({"status": "pass", "report": report["source_raw_path"]}, ensure_ascii=False))
            return 0
        if args.command == "validate-run":
            result = validate_run(paths.output_dir)
            print(json.dumps({"status": result["status"], "failures": result["failures"]}, ensure_ascii=False))
            return 0 if result["status"] == "pass" else 1
    except EvalError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    sys.exit(main())
