#!/usr/bin/env python3
"""Run calibration samples against the dddjango evaluator."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from eval_lib import EVAL_ROOT, WORKSPACE_ROOT, find_case, make_run_id, read_json, write_json
from score_outputs import score_text


CALIBRATION_ROOT = EVAL_ROOT / "calibration"


def evaluate_sample(sample: dict[str, Any]) -> dict[str, Any]:
    case = find_case(sample["case_id"])
    text = (CALIBRATION_ROOT / sample["path"]).read_text()
    score = score_text(case, sample["variant"], text)
    failures: list[str] = []

    expected_status = sample.get("expected_gate_status")
    if expected_status and score["gate_status"] != expected_status:
        failures.append(f"expected gate_status={expected_status}, got {score['gate_status']}")

    min_score = sample.get("min_score")
    if min_score is not None and score["total_score"] < min_score:
        failures.append(f"expected score >= {min_score}, got {score['total_score']}")

    max_score = sample.get("max_score")
    if max_score is not None and score["total_score"] > max_score:
        failures.append(f"expected score <= {max_score}, got {score['total_score']}")

    gate_statuses = {result["gate"]: result["status"] for result in score["gate_results"]}
    for gate in sample.get("required_pass_gates", []):
        if gate_statuses.get(gate) != "pass":
            failures.append(f"expected gate {gate} to pass")
    for gate in sample.get("required_fail_gates", []):
        if gate_statuses.get(gate) != "fail":
            failures.append(f"expected gate {gate} to fail")

    return {
        "sample_id": sample["id"],
        "case_id": sample["case_id"],
        "variant": sample["variant"],
        "status": "pass" if not failures else "fail",
        "failures": failures,
        "score": score,
    }


def run_calibration() -> dict[str, Any]:
    config = read_json(CALIBRATION_ROOT / "samples.json")
    results = [evaluate_sample(sample) for sample in config["samples"]]
    return {
        "status": "pass" if all(result["status"] == "pass" for result in results) else "fail",
        "sample_count": len(results),
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()

    report = run_calibration()
    if args.write_report:
        run_dir = WORKSPACE_ROOT / f"calibration-{make_run_id()}"
        write_json(run_dir / "calibration-report.json", report)
        print(f"캘리브레이션 리포트 생성: {run_dir / 'calibration-report.json'}")

    for result in report["results"]:
        mark = "✓" if result["status"] == "pass" else "✗"
        print(f"{mark} {result['sample_id']} score={result['score']['total_score']} gate={result['score']['gate_status']}")
        for failure in result["failures"]:
            print(f"  - {failure}")

    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
