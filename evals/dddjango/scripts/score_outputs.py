#!/usr/bin/env python3
"""Score dddjango purpose-fit evaluation outputs."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from eval_lib import (
    VARIANTS,
    clamp_score,
    hangul_ratio,
    load_cases,
    load_dimensions,
    load_gates,
    load_release_gates,
    ordered,
    regex_matches,
    run_dir_from_args,
    substring_matches,
    write_json,
)


def evaluate_gate(text: str, gate_id: str, gate: dict[str, Any]) -> dict[str, Any]:
    evidence: list[str] = []

    fail_if_any = substring_matches(gate.get("fail_if_any", []), text)
    fail_if_regex = regex_matches(gate.get("fail_if_regex", []), text)
    if fail_if_any or fail_if_regex:
        evidence.extend(fail_if_any)
        evidence.extend(fail_if_regex)
        return {
            "gate": gate_id,
            "status": "fail",
            "severity": gate.get("severity", "major"),
            "evidence": evidence,
            "message": gate.get("message", ""),
        }

    pass_if_all = gate.get("pass_if_all", [])
    missing_all = [pattern for pattern in pass_if_all if pattern.lower() not in text.lower()]
    if missing_all:
        return {
            "gate": gate_id,
            "status": "fail",
            "severity": gate.get("severity", "major"),
            "evidence": missing_all,
            "message": gate.get("message", ""),
        }

    pass_if_regex = gate.get("pass_if_regex", [])
    if pass_if_regex and not regex_matches(pass_if_regex, text):
        return {
            "gate": gate_id,
            "status": "fail",
            "severity": gate.get("severity", "major"),
            "evidence": pass_if_regex,
            "message": gate.get("message", ""),
        }

    pass_if_all_regex = gate.get("pass_if_all_regex", [])
    missing_all_regex = [
        pattern for pattern in pass_if_all_regex
        if not regex_matches([pattern], text)
    ]
    if missing_all_regex:
        return {
            "gate": gate_id,
            "status": "fail",
            "severity": gate.get("severity", "major"),
            "evidence": missing_all_regex,
            "message": gate.get("message", ""),
        }

    pass_if_ordered = gate.get("pass_if_ordered", [])
    if pass_if_ordered and not ordered(text, pass_if_ordered):
        return {
            "gate": gate_id,
            "status": "fail",
            "severity": gate.get("severity", "major"),
            "evidence": pass_if_ordered,
            "message": gate.get("message", ""),
        }

    pass_if_ordered_any = gate.get("pass_if_ordered_any", [])
    if pass_if_ordered_any and not any(ordered(text, sequence) for sequence in pass_if_ordered_any):
        return {
            "gate": gate_id,
            "status": "fail",
            "severity": gate.get("severity", "major"),
            "evidence": [" -> ".join(sequence) for sequence in pass_if_ordered_any],
            "message": gate.get("message", ""),
        }

    min_hangul_ratio = gate.get("min_hangul_ratio")
    if min_hangul_ratio is not None and hangul_ratio(text) < min_hangul_ratio:
        return {
            "gate": gate_id,
            "status": "fail",
            "severity": gate.get("severity", "major"),
            "evidence": [f"hangul_ratio={hangul_ratio(text):.3f}", f"minimum={min_hangul_ratio}"],
            "message": gate.get("message", ""),
        }

    return {
        "gate": gate_id,
        "status": "pass",
        "severity": gate.get("severity", "major"),
        "evidence": [],
        "message": gate.get("message", ""),
    }


def signal_results(case: dict[str, Any], text: str) -> dict[str, Any]:
    required_patterns = case.get("required_patterns", [])
    forbidden_patterns = case.get("forbidden_patterns", [])
    penalty_patterns = case.get("critical_forbidden_patterns", forbidden_patterns)
    required_hits = substring_matches(required_patterns, text)
    forbidden_hits = substring_matches(forbidden_patterns, text)
    penalty_hits = substring_matches(penalty_patterns, text)
    alternative_results = []
    for group in case.get("alternative_pattern_groups", []):
        patterns = group.get("patterns", [])
        hits = substring_matches(patterns, text)
        alternative_results.append({
            "label": group.get("label", ""),
            "status": "pass" if hits else "missing",
            "hits": hits,
            "accepted_patterns": patterns,
        })
    required_score = 100 if not required_patterns else 100 * (len(required_hits) / len(required_patterns))
    return {
        "score_kind": "automatic_signal",
        "required_patterns": {
            "hits": required_hits,
            "missing": [pattern for pattern in required_patterns if pattern not in required_hits],
            "score": clamp_score(required_score),
        },
        "forbidden_patterns": {
            "hits": forbidden_hits,
            "penalty_hits": penalty_hits,
            "score_penalty": min(100, 25 * len(penalty_hits)),
        },
        "alternative_pattern_groups": alternative_results,
        "expected_skills": {
            "values": case.get("expected_skills", []),
            "status": "manual_required",
        },
        "baseline": {
            "path": case.get("baseline"),
            "status": "manual_required",
        },
    }


def structural_checks(case: dict[str, Any], text: str) -> dict[str, Any]:
    checks: dict[str, dict[str, Any]] = {}
    dimensions = set(case.get("required_dimensions", []))

    if "django_ninja_api" in dimensions:
        patterns = {
            "router_instance": r"\bRouter\s*\(",
            "schema_class": r"\bclass\s+\w+\s*\(\s*Schema\s*\)",
            "router_decorator": r"@router\.(get|post|put|patch|delete)",
            "response_mapping": r"response\s*=\s*\{",
        }
        passed = [name for name, pattern in patterns.items() if regex_matches([pattern], text)]
        checks["django_ninja_api"] = {
            "status": "pass" if len(passed) == len(patterns) else "needs_review",
            "passed": passed,
            "missing": [name for name in patterns if name not in passed],
        }

    if "tdd_pytest" in dimensions:
        has_cycle = any(
            ordered(text, sequence)
            for sequence in [
                ["RED", "GREEN", "REFACTOR"],
                ["실패 테스트", "최소 구현", "리팩터링"],
                ["실패하는 테스트", "통과시키", "리팩터링"],
            ]
        )
        patterns = {
            "pytest": r"\bpytest\b|def\s+test_",
            "tdd_cycle": has_cycle,
            "failure_or_boundary": r"실패|경계|중복|idempot",
        }
        passed = [
            name for name, pattern in patterns.items()
            if (pattern is True) or (isinstance(pattern, str) and regex_matches([pattern], text))
        ]
        checks["tdd_pytest"] = {
            "status": "pass" if len(passed) == len(patterns) else "needs_review",
            "passed": passed,
            "missing": [name for name in patterns if name not in passed],
        }

    if "ddd_boundaries" in dimensions:
        terms = ["애그리거트", "값 객체", "도메인 서비스", "유스케이스", "도메인 이벤트", "불변식"]
        hits = substring_matches(terms, text)
        checks["ddd_boundaries"] = {
            "status": "pass" if len(hits) >= 2 else "needs_review",
            "passed": hits,
            "missing": [term for term in terms if term not in hits],
        }

    if "db_transaction" in dimensions:
        terms = ["transaction", "select_for_update", "idempotency", "unique", "locking", "version", "트랜잭션"]
        hits = substring_matches(terms, text)
        checks["db_transaction"] = {
            "status": "pass" if len(hits) >= 2 else "needs_review",
            "passed": hits,
            "missing": [term for term in terms if term not in hits],
        }

    return checks


def dimension_scores(case: dict[str, Any], text: str, gate_results: list[dict[str, Any]], gates: dict[str, Any]) -> dict[str, int]:
    scores: dict[str, int] = {}
    dimension_patterns = case.get("dimension_patterns", {})

    failed_dimensions: set[str] = set()
    for result in gate_results:
        if result["status"] != "fail":
            continue
        gate = gates.get(result["gate"], {})
        if result.get("severity") == "critical":
            failed_dimensions.update(gate.get("dimensions", []))

    for dimension in case.get("required_dimensions", []):
        patterns = dimension_patterns.get(dimension, [])
        if patterns:
            hits = substring_matches(patterns, text)
            score = 100 * (len(hits) / len(patterns))
        else:
            score = 100

        if dimension in failed_dimensions:
            score = 0

        score_penalty = signal_results(case, text)["forbidden_patterns"]["score_penalty"]
        if score_penalty:
            score -= score_penalty

        scores[dimension] = clamp_score(score)

    return scores


def weighted_total(scores: dict[str, int], dimensions: dict[str, Any]) -> int:
    if not scores:
        return 0
    total_weight = 0
    weighted = 0.0
    for dimension, score in scores.items():
        weight = dimensions.get(dimension, {}).get("weight", 1)
        total_weight += weight
        weighted += score * weight
    return clamp_score(weighted / total_weight)


def score_text(case: dict[str, Any], variant: str, text: str) -> dict[str, Any]:
    dimensions = load_dimensions()
    gates = load_gates()
    gate_results = [
        evaluate_gate(text, gate_id, gates[gate_id])
        for gate_id in case.get("critical_gates", [])
    ]
    signals = signal_results(case, text)
    critical_forbidden_patterns = case.get("critical_forbidden_patterns", case.get("forbidden_patterns", []))
    critical_forbidden_hits = substring_matches(critical_forbidden_patterns, text)
    if case.get("forbidden_is_critical") and critical_forbidden_hits:
        gate_results.append({
            "gate": "case_forbidden_patterns",
            "status": "fail",
            "severity": "critical",
            "evidence": critical_forbidden_hits,
            "message": "이 케이스에서는 forbidden pattern이 trigger 오염 또는 정책 위반을 의미한다.",
        })
    structures = structural_checks(case, text)
    scores = dimension_scores(case, text, gate_results, gates)
    total = weighted_total(scores, dimensions)
    failed = [result for result in gate_results if result["status"] == "fail"]
    gate_status = "fail" if failed else "pass"
    if gate_status == "fail":
        total = min(total, 59)

    rationale = "Critical gate 통과" if gate_status == "pass" else "Critical gate 실패: " + ", ".join(result["gate"] for result in failed)
    return {
        "case_id": case["id"],
        "variant": variant,
        "total_score": total,
        "score_kind": "automatic_signal",
        "automatic_confidence": "low",
        "manual_required": True,
        "gate_status": gate_status,
        "dimension_scores": scores,
        "signal_results": signals,
        "structural_checks": structures,
        "gate_results": gate_results,
        "rationale": rationale,
        "artifact": f"outputs/{case['id']}.{variant}.md",
    }


def missing_score(case: dict[str, Any], variant: str) -> dict[str, Any]:
    scores = {dimension: 0 for dimension in case.get("required_dimensions", [])}
    return {
        "case_id": case["id"],
        "variant": variant,
        "total_score": 0,
        "score_kind": "missing_output",
        "automatic_confidence": "high",
        "manual_required": False,
        "gate_status": "fail",
        "dimension_scores": scores,
        "signal_results": {
            "score_kind": "missing_output",
            "required_patterns": {"hits": [], "missing": case.get("required_patterns", []), "score": 0},
            "forbidden_patterns": {"hits": [], "score_penalty": 0},
            "alternative_pattern_groups": [],
            "expected_skills": {"values": case.get("expected_skills", []), "status": "not_evaluated"},
            "baseline": {"path": case.get("baseline"), "status": "not_evaluated"},
        },
        "structural_checks": {},
        "gate_results": [
            {
                "gate": "missing_output",
                "status": "fail",
                "severity": "critical",
                "evidence": [f"outputs/{case['id']}.{variant}.md"],
                "message": "평가 output 파일이 누락되면 실패로 처리한다.",
            }
        ],
        "rationale": "Output 누락",
        "artifact": f"outputs/{case['id']}.{variant}.md",
    }


def release_gate_status(summary: dict[str, Any], *, mode: str) -> dict[str, Any]:
    release_gates = load_release_gates()
    if mode != "live":
        return {
            "status": "not_applicable",
            "mode": mode,
            "message": "fixture/smoke run에는 release gate를 적용하지 않는다.",
            "results": [],
        }

    results: list[dict[str, Any]] = []
    by_variant = summary.get("by_variant", {})
    critical_failures = len(by_variant.get("with-dddjango", {}).get("critical_failures", []))
    max_failures = release_gates["critical_policy_failures"]["max_failures"]
    results.append({
        "gate": "critical_policy_failures",
        "status": "pass" if critical_failures <= max_failures else "fail",
        "actual": critical_failures,
        "expected": f"<= {max_failures}",
    })

    with_average = by_variant.get("with-dddjango", {}).get("average")
    min_average = release_gates["with_dddjango_average"]["minimum_average"]
    results.append({
        "gate": "with_dddjango_average",
        "status": "pass" if with_average is not None and with_average >= min_average else "fail",
        "actual": with_average,
        "expected": f">= {min_average}",
    })

    delta = summary.get("skill_value_delta")
    min_delta = release_gates["skill_value_delta"]["minimum_delta"]
    results.append({
        "gate": "skill_value_delta",
        "status": "pass" if delta is not None and delta >= min_delta else "fail",
        "actual": delta,
        "expected": f">= {min_delta}",
    })

    return {
        "status": "pass" if all(result["status"] == "pass" for result in results) else "fail",
        "mode": mode,
        "results": results,
    }


def summarize(scores: list[dict[str, Any]], *, mode: str = "unknown") -> dict[str, Any]:
    variants: dict[str, list[dict[str, Any]]] = {}
    for score in scores:
        variants.setdefault(score["variant"], []).append(score)

    by_variant: dict[str, Any] = {}
    for variant, items in variants.items():
        average = sum(item["total_score"] for item in items) / len(items) if items else 0
        failures = [
            {"case_id": item["case_id"], "rationale": item["rationale"]}
            for item in items
            if item["gate_status"] == "fail"
        ]
        by_variant[variant] = {
            "average": clamp_score(average),
            "case_count": len(items),
            "critical_failures": failures,
        }

    delta = None
    if "with-dddjango" in by_variant and "without-dddjango" in by_variant:
        delta = by_variant["with-dddjango"]["average"] - by_variant["without-dddjango"]["average"]

    summary = {
        "by_variant": by_variant,
        "skill_value_delta": delta,
        "scores": scores,
    }
    summary["release_gate_status"] = release_gate_status(summary, mode=mode)
    return summary


def score_run(run_dir: Path, suite: str | None = None, case_id: str | None = None) -> dict[str, Any]:
    cases = load_cases(suite)
    if case_id:
        cases = [case for case in cases if case["id"] == case_id]
    metadata_path = run_dir / "metadata.json"
    mode = "unknown"
    if metadata_path.exists():
        import json

        mode = json.loads(metadata_path.read_text()).get("mode", "unknown")
    scores: list[dict[str, Any]] = []
    for case in cases:
        for variant in VARIANTS:
            output_path = run_dir / "outputs" / f"{case['id']}.{variant}.md"
            if not output_path.exists():
                result = missing_score(case, variant)
            else:
                result = score_text(case, variant, output_path.read_text())
            scores.append(result)
            write_json(run_dir / "scores" / f"{case['id']}.{variant}.score.json", result)

    summary = summarize(scores, mode=mode)
    write_json(run_dir / "scores/summary.json", summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id")
    parser.add_argument("--latest", action="store_true")
    parser.add_argument("--suite")
    parser.add_argument("--case")
    args = parser.parse_args()

    run_dir = run_dir_from_args(args.run_id, args.latest)
    summary = score_run(run_dir, args.suite, args.case)
    print(f"채점 완료: {run_dir}")
    print(f"결과 수: {len(summary['scores'])}")
    release_status = summary.get("release_gate_status", {})
    if release_status.get("mode") == "live" and release_status.get("status") == "fail":
        print("live release gate 실패")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
