#!/usr/bin/env python3
"""Validate dddjango purpose-fit evaluation configuration."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from eval_lib import EVAL_ROOT, load_case_suites, load_dimensions, load_gates, read_json


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
            errors.extend(validate_case(case, dimensions=dimensions, gates=gates))

    read_json(EVAL_ROOT / "rubrics/release-gates.json")
    read_json(EVAL_ROOT / "rubrics/score-schema.json")

    if errors:
        raise ConfigError("\n".join(f"- {error}" for error in errors))


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
