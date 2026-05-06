#!/usr/bin/env python3
"""Validate dddjango purpose-fit evaluation configuration."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from eval_lib import EVAL_ROOT, ROOT, load_case_suites, load_dimensions, load_gates, load_reference_matrix, read_json


class ConfigError(Exception):
    pass


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_case(case: dict[str, Any], *, dimensions: dict[str, Any], gates: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    case_id = case.get("id", "<missing>")

    for field in [
        "id",
        "phase",
        "title",
        "prompt",
        "required_dimensions",
        "baseline",
        "expected_skills",
        "required_patterns",
        "dimension_patterns",
        "forbidden_patterns",
        "critical_gates",
    ]:
        require(field in case, f"{case_id}: missing field {field}", errors)

    required_dimensions = case.get("required_dimensions", [])
    require(isinstance(required_dimensions, list), f"{case_id}: required_dimensions must be a list", errors)
    for dimension in required_dimensions:
        require(dimension in dimensions, f"{case_id}: unknown dimension {dimension}", errors)

    baseline = case.get("baseline")
    if isinstance(baseline, str):
        require((EVAL_ROOT / baseline).exists(), f"{case_id}: missing baseline {baseline}", errors)
    else:
        errors.append(f"{case_id}: baseline must be a string")

    for list_field in ["expected_skills", "required_patterns", "forbidden_patterns", "critical_forbidden_patterns", "critical_gates"]:
        value = case.get(list_field, [])
        require(isinstance(value, list), f"{case_id}: {list_field} must be a list", errors)
        for item in value:
            require(isinstance(item, str), f"{case_id}: {list_field} entries must be strings", errors)

    if "anti_keyword_stuffing" in case:
        require(isinstance(case["anti_keyword_stuffing"], bool), f"{case_id}: anti_keyword_stuffing must be a boolean", errors)
    if "allow_legacy_drf_context" in case:
        require(isinstance(case["allow_legacy_drf_context"], bool), f"{case_id}: allow_legacy_drf_context must be a boolean", errors)

    dimension_patterns = case.get("dimension_patterns", {})
    require(isinstance(dimension_patterns, dict), f"{case_id}: dimension_patterns must be an object", errors)
    if isinstance(dimension_patterns, dict):
        for dimension, patterns in dimension_patterns.items():
            require(dimension in dimensions, f"{case_id}: unknown dimension_patterns key {dimension}", errors)
            require(isinstance(patterns, list), f"{case_id}: patterns for {dimension} must be a list", errors)
            for pattern in patterns:
                require(isinstance(pattern, str), f"{case_id}: pattern entries for {dimension} must be strings", errors)

    for group in case.get("alternative_pattern_groups", []):
        require(isinstance(group, dict), f"{case_id}: alternative_pattern_groups entries must be objects", errors)
        require(isinstance(group.get("label"), str), f"{case_id}: alternative pattern group label must be a string", errors)
        patterns = group.get("patterns", [])
        require(isinstance(patterns, list), f"{case_id}: alternative pattern group patterns must be a list", errors)
        for pattern in patterns:
            require(isinstance(pattern, str), f"{case_id}: alternative pattern entries must be strings", errors)

    for gate in case.get("critical_gates", []):
        require(gate in gates, f"{case_id}: unknown gate {gate}", errors)

    return errors


def validate_all() -> None:
    errors: list[str] = []
    dimensions = load_dimensions()
    gates = load_gates()
    suite_files = sorted((EVAL_ROOT / "cases").glob("*.json"))

    require(bool(dimensions), "rubrics/dimensions.json must not be empty", errors)
    require(bool(gates), "rubrics/gates.json must not be empty", errors)
    require(bool(suite_files), "cases/*.json must exist", errors)

    seen_ids: set[str] = set()
    case_by_id: dict[str, dict[str, Any]] = {}
    for suite_path in suite_files:
        suite = read_json(suite_path)
        require("suite" in suite, f"{suite_path.name}: missing suite", errors)
        cases = suite.get("cases", [])
        require(isinstance(cases, list), f"{suite_path.name}: cases must be a list", errors)
        for case in cases:
            case_id = case.get("id")
            require(case_id not in seen_ids, f"duplicate case id: {case_id}", errors)
            if case_id:
                seen_ids.add(case_id)
                case_by_id[case_id] = case
            errors.extend(validate_case(case, dimensions=dimensions, gates=gates))

    read_json(EVAL_ROOT / "rubrics/release-gates.json")
    read_json(EVAL_ROOT / "rubrics/score-schema.json")
    errors.extend(validate_reference_matrix(case_by_id))

    if errors:
        raise ConfigError("\n".join(f"- {error}" for error in errors))


def validate_reference_matrix(case_by_id: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    matrix = load_reference_matrix()
    entries = matrix.get("cases", {})
    require(isinstance(entries, dict), "reference-matrix.json: cases must be an object", errors)
    if not isinstance(entries, dict):
        return errors

    matrix_ids = set(entries)
    case_ids = set(case_by_id)
    for case_id in sorted(case_ids - matrix_ids):
        errors.append(f"reference-matrix.json: missing case {case_id}")
    for case_id in sorted(matrix_ids - case_ids):
        errors.append(f"reference-matrix.json: unknown case {case_id}")

    for case_id, entry in entries.items():
        if not isinstance(entry, dict):
            errors.append(f"reference-matrix.json: {case_id} entry must be an object")
            continue

        expected_skills = entry.get("expected_skills")
        require(isinstance(expected_skills, list), f"reference-matrix.json: {case_id} expected_skills must be a list", errors)
        if case_id in case_by_id and isinstance(expected_skills, list):
            require(
                expected_skills == case_by_id[case_id].get("expected_skills", []),
                f"reference-matrix.json: {case_id} expected_skills must match case definition",
                errors,
            )

        reference_paths = entry.get("reference_paths", [])
        guard_paths = entry.get("guard_paths", [])
        for field_name, paths in [("reference_paths", reference_paths), ("guard_paths", guard_paths)]:
            require(isinstance(paths, list), f"reference-matrix.json: {case_id} {field_name} must be a list", errors)
            if not isinstance(paths, list):
                continue
            for path in paths:
                require(isinstance(path, str), f"reference-matrix.json: {case_id} {field_name} entries must be strings", errors)
                if isinstance(path, str):
                    require((ROOT / path).exists(), f"reference-matrix.json: {case_id} missing path {path}", errors)

        reference_rules = entry.get("reference_rules", [])
        require(isinstance(reference_rules, list), f"reference-matrix.json: {case_id} reference_rules must be a list", errors)
        if isinstance(reference_rules, list):
            for rule in reference_rules:
                require(isinstance(rule, str), f"reference-matrix.json: {case_id} reference_rules entries must be strings", errors)

        require(
            isinstance(entry.get("diagnostic_use"), str) and bool(entry.get("diagnostic_use", "").strip()),
            f"reference-matrix.json: {case_id} diagnostic_use is required",
            errors,
        )

    return errors


def main() -> int:
    try:
        validate_all()
    except Exception as exc:
        print("dddjango 평가 설정 검증 실패", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 1

    print("dddjango 평가 설정 검증 성공")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
