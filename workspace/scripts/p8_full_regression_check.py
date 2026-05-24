#!/usr/bin/env python3
"""P8 full-regression aggregate validator.

This script does not run model-backed evals. It validates the final P8 raw,
report, validation, installed-runtime, and review artifacts after those runs
exist.
"""

from __future__ import annotations

import argparse
import filecmp
import json
import re
import sys
from pathlib import Path
from typing import Any

import p5_individual_eval as base


class P8CheckError(Exception):
    """Raised for command contract errors."""


def read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def raw_digest(raw: dict[str, Any]) -> str:
    return base.digest_for_data({key: value for key, value in raw.items() if key != "raw_digest"})


def status_count(raw: dict[str, Any], status: str) -> int:
    counts = raw.get("status_counts")
    return int(counts.get(status, 0)) if isinstance(counts, dict) else 0


def metadata_current(raw: dict[str, Any], repo_root: Path) -> tuple[bool, list[str]]:
    mismatches: list[str] = []
    current_metadata: dict[str, str] = {}
    metadata = raw.get("metadata_digests")
    if not isinstance(metadata, dict):
        return False, ["metadata-digests-missing"]
    for key in sorted(metadata):
        path = base.metadata_path_for_key(str(key), repo_root)
        if not path.is_file():
            mismatches.append(f"metadata-file-missing:{key}")
            continue
        current_metadata[str(key)] = base.sha256_file(path)
    if current_metadata != metadata:
        mismatches.append("metadata-digest-mismatch")
    if base.digest_for_data(metadata) != raw.get("metadata_digest"):
        mismatches.append("metadata-digest-field-mismatch")
    return not mismatches, mismatches


def check_targeted_suite(output_dir: Path, raw: dict[str, Any]) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    targeted_path = output_dir / "raw" / "targeted-suite.json"
    if not targeted_path.is_file():
        return [{"kind": "targeted-suite-missing", "path": base.safe_artifact_path(targeted_path)}]
    targeted = read_json(targeted_path)
    if targeted.get("model_backed") is not True:
        failures.append({"kind": "targeted-suite-not-model-backed"})
    if targeted.get("status") != "pass":
        failures.append({"kind": "targeted-suite-not-pass", "actual": targeted.get("status")})
    if not isinstance(targeted.get("iterations"), int) or targeted.get("iterations") < 2:
        failures.append({"kind": "targeted-suite-iterations-insufficient", "actual": targeted.get("iterations")})
    if targeted.get("variance_status") != "stable-pass":
        failures.append({"kind": "targeted-suite-flaky-or-unclassified", "actual": targeted.get("variance_status")})
    if targeted.get("variants") != raw.get("variants"):
        failures.append({"kind": "targeted-suite-variant-mismatch", "targeted": targeted.get("variants"), "raw": raw.get("variants")})
    for run in targeted.get("runs", []):
        if not isinstance(run, dict) or run.get("status") != "pass":
            failures.append({"kind": "targeted-suite-run-not-pass", "run": run})
    return failures


def check_eval_output(output_dir: Path, repo_root: Path, label: str) -> dict[str, Any]:
    raw_path = output_dir / "raw" / "run.json"
    report_path = output_dir / "report" / "report.json"
    report_html_path = output_dir / "report" / "report.html"
    validation_path = output_dir / "validation" / "validate-run.json"
    failures: list[dict[str, Any]] = []

    for kind, path in (
        ("raw-missing", raw_path),
        ("report-json-missing", report_path),
        ("report-html-missing", report_html_path),
        ("validation-missing", validation_path),
    ):
        if not path.is_file():
            failures.append({"kind": kind, "path": base.safe_artifact_path(path)})
    if failures:
        return {"label": label, "status": "fail", "failures": failures}

    raw = read_json(raw_path)
    report = read_json(report_path)
    validation = read_json(validation_path)
    computed_raw_digest = raw_digest(raw)

    if raw.get("status") != "pass":
        failures.append({"kind": "raw-status-not-pass", "actual": raw.get("status")})
    if raw.get("model_backed") is not True:
        failures.append({"kind": "raw-not-model-backed"})
    if validation.get("status") != "pass" or validation.get("failures") not in ([], None):
        failures.append({"kind": "validate-run-not-pass", "status": validation.get("status"), "failures": validation.get("failures")})
    if raw.get("raw_digest") != computed_raw_digest:
        failures.append({"kind": "raw-digest-mismatch"})
    if report.get("source_raw_digest") != computed_raw_digest:
        failures.append({"kind": "stale-report", "expected": computed_raw_digest, "actual": report.get("source_raw_digest")})
    if validation.get("raw_digest") != computed_raw_digest:
        failures.append({"kind": "validation-raw-digest-mismatch", "expected": computed_raw_digest, "actual": validation.get("raw_digest")})
    if report.get("run_id") != raw.get("run_id"):
        failures.append({"kind": "report-run-id-mismatch", "raw": raw.get("run_id"), "report": report.get("run_id")})
    if report.get("status_counts") != raw.get("status_counts"):
        failures.append({"kind": "report-status-count-mismatch"})
    if status_count(raw, "not-scored"):
        failures.append({"kind": "not-scored-present", "count": status_count(raw, "not-scored")})
    non_pass = status_count(raw, "partial") + status_count(raw, "fail") + status_count(raw, "not-scored")
    if non_pass:
        failures.append({"kind": "non-pass-result-present", "count": non_pass})

    forbidden_semantics = {
        "missing-oracle",
        "malformed-oracle",
        "missing-answer",
        "malformed-answer",
        "expected-outcomes-conflict",
    }
    semantic_hits = [
        item
        for result in raw.get("results", [])
        for item in result.get("failure_semantics", [])
        if item in forbidden_semantics
    ]
    if semantic_hits:
        failures.append({"kind": "missing-malformed-or-conflict-present", "count": len(semantic_hits)})

    leakage_findings = base.scan_persisted_artifacts_for_local_leakage(output_dir)
    if leakage_findings:
        failures.append({"kind": "local-path-or-private-leakage-present", "count": len(leakage_findings)})

    metadata_ok, metadata_failures = metadata_current(raw, repo_root)
    if not metadata_ok:
        failures.extend({"kind": item} for item in metadata_failures)

    failures.extend(check_targeted_suite(output_dir, raw))

    report_html = report_html_path.read_text(encoding="utf-8", errors="replace")
    if str(raw.get("run_id")) not in report_html:
        failures.append({"kind": "report-html-run-id-missing"})
    if computed_raw_digest not in report_html:
        failures.append({"kind": "report-html-raw-digest-missing"})
    if report.get("report_html_digest") != base.sha256_file(report_html_path):
        failures.append({"kind": "report-html-digest-mismatch"})

    return {
        "label": label,
        "status": "fail" if failures else "pass",
        "run_id": raw.get("run_id"),
        "raw_path": base.safe_artifact_path(raw_path),
        "report_path": base.safe_artifact_path(report_path),
        "validation_path": base.safe_artifact_path(validation_path),
        "raw_digest": computed_raw_digest,
        "metadata_digest": raw.get("metadata_digest"),
        "status_counts": raw.get("status_counts"),
        "case_count": raw.get("case_count"),
        "result_count": raw.get("result_count"),
        "model_backed": raw.get("model_backed"),
        "leakage_findings": leakage_findings,
        "failures": failures,
    }


def recursive_file_map(root: Path) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        mapping[path.relative_to(root).as_posix()] = base.sha256_file(path)
    return mapping


def check_p7_current(
    *,
    repo_root: Path,
    source_plugin_root: Path,
    installed_cache_root: Path,
    p7_runtime_analysis: Path,
    p7_manifest_validation: Path,
) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    if not source_plugin_root.is_dir():
        failures.append({"kind": "source-plugin-root-missing", "path": source_plugin_root.as_posix()})
    if not installed_cache_root.is_dir():
        failures.append({"kind": "installed-cache-root-missing", "path": installed_cache_root.as_posix()})
    if failures:
        return {"status": "fail", "failures": failures}

    source_files = recursive_file_map(source_plugin_root)
    cache_files = recursive_file_map(installed_cache_root)
    if source_files != cache_files:
        diff = filecmp.dircmp(source_plugin_root, installed_cache_root)
        failures.append({"kind": "source-cache-file-digest-mismatch", "left_only": diff.left_only, "right_only": diff.right_only})

    runtime = read_json(p7_runtime_analysis)
    if runtime.get("status") != "pass":
        failures.append({"kind": "p7-runtime-analysis-not-pass", "actual": runtime.get("status")})
    expected_counts = {
        "case_count": 26,
        "family_count": 13,
        "happy_count": 13,
        "exclusion_count": 13,
        "failure_count": 0,
        "routing_pass_count": 26,
        "cache_path_pass_count": 26,
        "final_answer_pass_count": 26,
    }
    for key, expected in expected_counts.items():
        if runtime.get(key) != expected:
            failures.append({"kind": "p7-runtime-count-mismatch", "field": key, "expected": expected, "actual": runtime.get(key)})

    manifest = read_json(p7_manifest_validation)
    source_manifest = source_plugin_root / ".codex-plugin" / "plugin.json"
    cache_manifest = installed_cache_root / ".codex-plugin" / "plugin.json"
    if manifest.get("status") != "pass":
        failures.append({"kind": "p7-manifest-validation-not-pass", "actual": manifest.get("status")})
    if manifest.get("source_manifest_sha256") != base.sha256_file(source_manifest):
        failures.append({"kind": "p7-source-manifest-digest-stale"})
    if manifest.get("cache_manifest_sha256") != base.sha256_file(cache_manifest):
        failures.append({"kind": "p7-cache-manifest-digest-stale"})

    return {
        "status": "fail" if failures else "pass",
        "source_plugin_root": base.safe_artifact_path(source_plugin_root, repo_root),
        "installed_cache_root": "installed-cache:.",
        "source_cache_file_count": len(source_files),
        "runtime_analysis_path": base.safe_artifact_path(p7_runtime_analysis, repo_root),
        "manifest_validation_path": base.safe_artifact_path(p7_manifest_validation, repo_root),
        "failures": failures,
    }


def parse_count(label: str, text: str) -> int | None:
    pattern = re.compile(rf"{re.escape(label)}\s*[:=]?\s*(\d+)", re.IGNORECASE)
    match = pattern.search(text)
    return int(match.group(1)) if match else None


def check_review_gate(review_raw: Path, review_summary: Path, repo_root: Path) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    if not review_raw.is_file():
        failures.append({"kind": "review-raw-missing", "path": base.safe_artifact_path(review_raw, repo_root)})
    if not review_summary.is_file():
        failures.append({"kind": "review-summary-missing", "path": base.safe_artifact_path(review_summary, repo_root)})
    if failures:
        return {"status": "fail", "failures": failures}

    summary = review_summary.read_text(encoding="utf-8")
    blocker = parse_count("Blocker", summary)
    major = parse_count("Major", summary)
    open_minor = parse_count("Open Minor", summary)
    if blocker != 0:
        failures.append({"kind": "review-blocker-open", "actual": blocker})
    if major != 0:
        failures.append({"kind": "review-major-open", "actual": major})
    if open_minor != 0:
        failures.append({"kind": "review-minor-open", "actual": open_minor})
    if "raw review output path" not in summary.casefold() and base.safe_artifact_path(review_raw, repo_root) not in summary:
        failures.append({"kind": "review-summary-raw-link-missing"})
    return {
        "status": "fail" if failures else "pass",
        "raw_path": base.safe_artifact_path(review_raw, repo_root),
        "summary_path": base.safe_artifact_path(review_summary, repo_root),
        "raw_digest": base.sha256_file(review_raw),
        "summary_digest": base.sha256_file(review_summary),
        "finding_counts": {"Blocker": blocker, "Major": major, "Open Minor": open_minor},
        "failures": failures,
    }


def check_full_regression(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve()
    p5 = check_eval_output((repo_root / args.p5_output_dir).resolve(), repo_root, "p5-individual-skills")
    p6 = check_eval_output((repo_root / args.p6_output_dir).resolve(), repo_root, "p6-integration-flows")
    p7 = check_p7_current(
        repo_root=repo_root,
        source_plugin_root=(repo_root / args.source_plugin_root).resolve(),
        installed_cache_root=Path(args.installed_cache_root).resolve(),
        p7_runtime_analysis=(repo_root / args.p7_runtime_analysis).resolve(),
        p7_manifest_validation=(repo_root / args.p7_manifest_validation).resolve(),
    )
    review = check_review_gate((repo_root / args.review_raw).resolve(), (repo_root / args.review_summary).resolve(), repo_root)
    failures = []
    for section_name, section in (("p5", p5), ("p6", p6), ("p7", p7), ("review", review)):
        if section.get("status") != "pass":
            failures.append({"section": section_name, "failures": section.get("failures", [])})
    result = {
        "schema_version": "p8-full-regression-check/v1",
        "status": "fail" if failures else "pass",
        "p5": p5,
        "p6": p6,
        "p7": p7,
        "review": review,
        "failures": failures,
    }
    return result


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--p5-output-dir", default="workspace/develop/eval/runs/p8-full-regression-p5-model-installed-runtime")
    parser.add_argument("--p6-output-dir", default="workspace/develop/eval/runs/p8-full-regression-p6-model-installed-runtime")
    parser.add_argument("--source-plugin-root", default="dddjango")
    parser.add_argument("--installed-cache-root", default="/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10")
    parser.add_argument(
        "--p7-runtime-analysis",
        default="workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-runtime-analysis-raw.json",
    )
    parser.add_argument(
        "--p7-manifest-validation",
        default="workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-manifest-validation-raw.json",
    )
    parser.add_argument("--review-raw", required=True)
    parser.add_argument("--review-summary", required=True)
    parser.add_argument("--output")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = check_full_regression(args)
        if args.output:
            write_json(Path(args.output), result)
        print(json.dumps({"status": result["status"], "failures": result["failures"]}, ensure_ascii=False))
        return 0 if result["status"] == "pass" else 1
    except (P8CheckError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
