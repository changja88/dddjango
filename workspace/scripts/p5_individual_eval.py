#!/usr/bin/env python3
"""P5 individual-skill fixture scorer for the dddjango rebuild plan.

This runner is intentionally local and deterministic. It scores the P5
individual-skill matrix against explicit answer/oracle fixture data, records
current-file digests in run metadata, and validates raw/report consistency.
It is not model-backed runtime evidence.
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


class EvalError(Exception):
    """Raised for command contract errors."""


@dataclass(frozen=True)
class Paths:
    fixture_root: Path
    output_dir: Path
    repo_root: Path


def read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest_for_data(data: Any) -> str:
    return sha256_text(canonical_json(data))


def load_cases(fixture_root: Path) -> list[dict[str, Any]]:
    path = fixture_root / "cases.json"
    cases = read_json(path)
    if not isinstance(cases, list):
        raise EvalError("cases.json must contain a list")
    return cases


def case_by_id(fixture_root: Path, case_id: str) -> dict[str, Any]:
    for case in load_cases(fixture_root):
        if case.get("id") == case_id:
            return case
    raise EvalError(f"case not found: {case_id}")


def metadata_digest_manifest(paths: Paths) -> dict[str, str]:
    roots = [
        paths.fixture_root / "cases.json",
        paths.repo_root / "workspace/plan/phases/p1-5-usage-cards/cards/20260522-230605-p1-5-skill-usage-cards-evidence.md",
        paths.repo_root / "workspace/plan/governance/eval_protocol.md",
        paths.repo_root / "workspace/scripts/p5_individual_eval.py",
    ]
    manifest: dict[str, str] = {}
    for path in roots:
        manifest[path.relative_to(paths.repo_root).as_posix()] = sha256_file(path)
    for path in sorted((paths.repo_root / "dddjango/skills").glob("*/SKILL.md")):
        manifest[path.relative_to(paths.repo_root).as_posix()] = sha256_file(path)
    return manifest


def display_path(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()


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
        seen[str(key)] = value
    return None


def score_variant(*, case: dict[str, Any], variant: str) -> dict[str, Any]:
    case_id = str(case.get("id"))
    result: dict[str, Any] = {
        "case_id": case_id,
        "variant": variant,
        "surface": case.get("surface"),
        "skill_under_test": case.get("skill_under_test"),
        "expected_loaded_skill": None,
        "actual_loaded_skill": None,
        "status": "not-scored",
        "score": None,
        "failure_semantics": [],
        "checks": {},
    }

    conflict = expected_outcome_conflict(case)
    if conflict:
        result["failure_semantics"].append(conflict)
        return result

    oracle = case.get("oracle")
    answers = case.get("answers")
    if not isinstance(oracle, dict):
        result["failure_semantics"].append("malformed-oracle")
        return result
    if not isinstance(answers, dict) or variant not in answers:
        result["failure_semantics"].append("missing-answer")
        return result
    answer = answers[variant]
    if not isinstance(answer, dict):
        result["failure_semantics"].append("malformed-answer")
        return result

    required_claims = oracle.get("required_claims")
    if not isinstance(required_claims, list) or not all(isinstance(item, str) for item in required_claims):
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
    actual_loaded_skill = answer.get("loaded_skill")
    result["expected_loaded_skill"] = expected_loaded_skill
    result["actual_loaded_skill"] = actual_loaded_skill
    if expected_loaded_skill is not None:
        loaded_skill_ok = actual_loaded_skill == expected_loaded_skill
        result["checks"]["loaded_skill"] = {
            "expected": expected_loaded_skill,
            "actual": actual_loaded_skill,
            "ok": loaded_skill_ok,
        }
        if not loaded_skill_ok:
            result["failure_semantics"].append("wrong-routing")

    if answer.get("overclaims"):
        result["failure_semantics"].append("forbidden-overclaim")

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


def run_one(paths: Paths, case_id: str, variant: str, run_id: str) -> dict[str, Any]:
    if variant not in VARIANTS:
        raise EvalError(f"variant must be one of {', '.join(VARIANTS)}")
    case = case_by_id(paths.fixture_root, case_id)
    result = score_variant(case=case, variant=variant)
    result["run_id"] = run_id
    result["metadata_digests"] = metadata_digest_manifest(paths)
    result["metadata_digest"] = digest_for_data(result["metadata_digests"])
    write_json(paths.output_dir / "raw" / "one.json", result)
    return result


def run_bucket(paths: Paths, bucket: str, run_id: str) -> dict[str, Any]:
    cases = [case for case in load_cases(paths.fixture_root) if case.get("bucket") == bucket]
    if not cases:
        raise EvalError(f"bucket not found or empty: {bucket}")

    results: list[dict[str, Any]] = []
    for case in cases:
        for variant in VARIANTS:
            results.append(score_variant(case=case, variant=variant))

    status_counts: dict[str, int] = {"pass": 0, "partial": 0, "fail": 0, "not-scored": 0}
    for result in results:
        status_counts[result["status"]] += 1

    hard_failures = [result for result in results if result["status"] in FAIL_STATUSES]
    raw = {
        "schema_version": "p5-individual-eval-run/v1",
        "run_id": run_id,
        "bucket": bucket,
        "fixture_root": paths.fixture_root.relative_to(paths.repo_root).as_posix(),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "variants": list(VARIANTS),
        "run_mode": "fixture-scored-p5-preflight",
        "model_backed": False,
        "runtime_parity_precondition": "not-complete-in-current-phase-status",
        "status": "fail" if hard_failures else "pass",
        "status_counts": status_counts,
        "hard_failure_count": len(hard_failures),
        "case_count": len(cases),
        "result_count": len(results),
        "metadata_digests": metadata_digest_manifest(paths),
        "results": results,
    }
    raw["metadata_digest"] = digest_for_data(raw["metadata_digests"])
    raw["raw_digest"] = digest_for_data({key: value for key, value in raw.items() if key != "raw_digest"})
    write_json(paths.output_dir / "raw" / "run.json", raw)
    return raw


def run_targeted_suite(paths: Paths, bucket: str, run_id: str, iterations: int) -> dict[str, Any]:
    if iterations < 1:
        raise EvalError("iterations must be >= 1")
    runs = []
    for iteration in range(1, iterations + 1):
        iteration_run_id = f"{run_id}-targeted-{iteration}"
        raw = run_bucket(paths, bucket, iteration_run_id)
        iteration_path = paths.output_dir / "raw" / f"targeted-run-{iteration}.json"
        write_json(iteration_path, raw)
        runs.append(
            {
                "iteration": iteration,
                "run_id": iteration_run_id,
                "artifact": display_path(iteration_path, paths.repo_root),
                "status": raw["status"],
                "status_counts": raw["status_counts"],
                "metadata_digest": raw["metadata_digest"],
            }
        )
    summary = {
        "schema_version": "p5-individual-targeted-suite/v1",
        "run_id": run_id,
        "bucket": bucket,
        "iterations": iterations,
        "status": "pass" if all(run["status"] == "pass" for run in runs) else "fail",
        "runs": runs,
    }
    write_json(paths.output_dir / "raw" / "targeted-suite.json", summary)
    return summary


def render_report(output_dir: Path) -> dict[str, Any]:
    raw_path = output_dir / "raw" / "run.json"
    if not raw_path.is_file():
        raise EvalError(f"missing raw run artifact: {raw_path}")
    raw = read_json(raw_path)
    source_digest = digest_for_data({key: value for key, value in raw.items() if key != "raw_digest"})
    report_results: list[dict[str, Any]] = []
    rows = []
    for result in raw.get("results", []):
        semantics = ", ".join(result["failure_semantics"]) or "-"
        rows.append(
            "<tr>"
            f"<td>{html.escape(result['case_id'])}</td>"
            f"<td>{html.escape(result['variant'])}</td>"
            f"<td>{html.escape(str(result.get('surface')))}</td>"
            f"<td>{html.escape(str(result.get('skill_under_test')))}</td>"
            f"<td>{html.escape(result['status'])}</td>"
            f"<td>{html.escape(str(result.get('actual_loaded_skill')))}</td>"
            f"<td>{html.escape(semantics)}</td>"
            "</tr>"
        )
        report_results.append(
            {
                "case_id": result["case_id"],
                "variant": result["variant"],
                "surface": result.get("surface"),
                "skill_under_test": result.get("skill_under_test"),
                "status": result["status"],
                "actual_loaded_skill": result.get("actual_loaded_skill"),
                "failure_semantics": result["failure_semantics"],
            }
        )

    report_json = {
        "schema_version": "p5-individual-eval-report/v1",
        "run_id": raw["run_id"],
        "source_raw_path": raw_path.as_posix(),
        "source_raw_digest": source_digest,
        "status_counts": raw["status_counts"],
        "model_backed": raw.get("model_backed"),
        "runtime_parity_precondition": raw.get("runtime_parity_precondition"),
        "metadata_digest": raw.get("metadata_digest"),
        "results": report_results,
    }
    write_json(output_dir / "report" / "report.json", report_json)
    html_text = "\n".join(
        [
            "<!doctype html>",
            "<html><head><meta charset=\"utf-8\"><title>dddjango P5 individual eval report</title></head>",
            "<body>",
            f"<h1>{html.escape(raw['run_id'])}</h1>",
            f"<p>Model backed: {html.escape(str(raw.get('model_backed')))}</p>",
            f"<p>Runtime parity precondition: {html.escape(str(raw.get('runtime_parity_precondition')))}</p>",
            f"<p>Raw digest: {html.escape(source_digest)}</p>",
            "<table>",
            "<thead><tr><th>case</th><th>variant</th><th>surface</th><th>skill under test</th><th>status</th><th>actual loaded skill</th><th>failure semantics</th></tr></thead>",
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


def validate_run(output_dir: Path, repo_root: Path) -> dict[str, Any]:
    raw_path = output_dir / "raw" / "run.json"
    report_path = output_dir / "report" / "report.json"
    failures: list[dict[str, Any]] = []
    if not raw_path.is_file():
        failures.append({"kind": "missing-raw-artifact", "path": raw_path.as_posix()})
    if not report_path.is_file():
        failures.append({"kind": "missing-report-artifact", "path": report_path.as_posix()})
    if failures:
        result = {"schema_version": "p5-individual-eval-validation/v1", "status": "fail", "failures": failures}
        write_json(output_dir / "validation" / "validate-run.json", result)
        return result

    raw = read_json(raw_path)
    report = read_json(report_path)
    raw_digest = digest_for_data({key: value for key, value in raw.items() if key != "raw_digest"})
    if raw.get("raw_digest") != raw_digest:
        failures.append({"kind": "raw-digest-mismatch"})
    if report.get("source_raw_digest") != raw_digest:
        failures.append({"kind": "stale-report", "expected": raw_digest, "actual": report.get("source_raw_digest")})
    if report.get("status_counts") != raw.get("status_counts"):
        failures.append({"kind": "report-status-count-mismatch"})

    raw_result_keys = {
        (item["case_id"], item["variant"]): (
            item["surface"],
            item["skill_under_test"],
            item["status"],
            item["actual_loaded_skill"],
            tuple(item["failure_semantics"]),
        )
        for item in raw.get("results", [])
    }
    report_result_keys = {
        (item["case_id"], item["variant"]): (
            item["surface"],
            item["skill_under_test"],
            item["status"],
            item["actual_loaded_skill"],
            tuple(item["failure_semantics"]),
        )
        for item in report.get("results", [])
    }
    if raw_result_keys != report_result_keys:
        failures.append({"kind": "report-raw-result-mismatch"})

    not_scored = [key for key, value in raw_result_keys.items() if value[2] == "not-scored"]
    if not_scored:
        failures.append({"kind": "not-scored-present", "count": len(not_scored)})
    non_pass = [key for key, value in raw_result_keys.items() if value[2] != "pass"]
    if non_pass:
        failures.append({"kind": "non-pass-result-present", "count": len(non_pass)})

    missing_or_malformed = [
        item
        for result in raw.get("results", [])
        for item in result.get("failure_semantics", [])
        if item.startswith("missing-") or item.startswith("malformed-")
    ]
    if missing_or_malformed:
        failures.append({"kind": "missing-or-malformed-oracle-or-answer", "count": len(missing_or_malformed)})

    current_metadata: dict[str, str] = {}
    missing_metadata_files = []
    for rel_path in sorted(raw.get("metadata_digests", {})):
        path = repo_root / rel_path
        if not path.is_file():
            missing_metadata_files.append(rel_path)
            continue
        current_metadata[rel_path] = sha256_file(path)
    if missing_metadata_files:
        failures.append({"kind": "metadata-file-missing", "paths": missing_metadata_files})
    if current_metadata != raw.get("metadata_digests"):
        failures.append({"kind": "metadata-digest-mismatch"})
    if digest_for_data(raw.get("metadata_digests", {})) != raw.get("metadata_digest"):
        failures.append({"kind": "metadata-digest-field-mismatch"})

    result = {
        "schema_version": "p5-individual-eval-validation/v1",
        "status": "fail" if failures else "pass",
        "raw_path": raw_path.as_posix(),
        "report_path": report_path.as_posix(),
        "raw_digest": raw_digest,
        "metadata_digest": raw.get("metadata_digest"),
        "status_counts": raw.get("status_counts"),
        "case_count": raw.get("case_count"),
        "result_count": raw.get("result_count"),
        "model_backed": raw.get("model_backed"),
        "runtime_parity_precondition": raw.get("runtime_parity_precondition"),
        "failures": failures,
    }
    write_json(output_dir / "validation" / "validate-run.json", result)
    return result


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture-root", default="workspace/develop/eval/fixtures/individual-skills")
    parser.add_argument("--output-dir", default="workspace/develop/eval/runs/p5-individual-skills-fixture")
    parser.add_argument("--repo-root", default=".")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_one_parser = subparsers.add_parser("run-one")
    run_one_parser.add_argument("--case-id", required=True)
    run_one_parser.add_argument("--variant", choices=VARIANTS, required=True)
    run_one_parser.add_argument("--run-id", default="p5-individual-skills-targeted")

    run_bucket_parser = subparsers.add_parser("run-bucket")
    run_bucket_parser.add_argument("--bucket", default="individual-skills")
    run_bucket_parser.add_argument("--run-id", default="p5-individual-skills-fixture")

    targeted_parser = subparsers.add_parser("run-targeted-suite")
    targeted_parser.add_argument("--bucket", default="individual-skills")
    targeted_parser.add_argument("--run-id", default="p5-individual-skills-fixture")
    targeted_parser.add_argument("--iterations", type=int, default=2)

    subparsers.add_parser("render-report")
    subparsers.add_parser("validate-run")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    paths = Paths(
        fixture_root=(repo_root / args.fixture_root).resolve(),
        output_dir=(repo_root / args.output_dir).resolve(),
        repo_root=repo_root,
    )
    try:
        if args.command == "run-one":
            result = run_one(paths, args.case_id, args.variant, args.run_id)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result["status"] in PASS_STATUSES else 1
        if args.command == "run-bucket":
            raw = run_bucket(paths, args.bucket, args.run_id)
            print(json.dumps({"status": raw["status"], "status_counts": raw["status_counts"]}, ensure_ascii=False))
            return 0 if raw["status"] == "pass" else 1
        if args.command == "run-targeted-suite":
            summary = run_targeted_suite(paths, args.bucket, args.run_id, args.iterations)
            print(json.dumps({"status": summary["status"], "iterations": summary["iterations"]}, ensure_ascii=False))
            return 0 if summary["status"] == "pass" else 1
        if args.command == "render-report":
            report = render_report(paths.output_dir)
            print(json.dumps({"status": "pass", "report": report["source_raw_path"]}, ensure_ascii=False))
            return 0
        if args.command == "validate-run":
            result = validate_run(paths.output_dir, repo_root)
            print(json.dumps({"status": result["status"], "failures": result["failures"]}, ensure_ascii=False))
            return 0 if result["status"] == "pass" else 1
    except EvalError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    sys.exit(main())
