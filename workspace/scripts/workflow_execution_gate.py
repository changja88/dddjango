#!/usr/bin/env python3
"""Deterministic workflow execution-mode gates for dddjango evals."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


ALWAYS_HARD_FAIL_MODES = {"false_actual_claim", "actual_subagent_incomplete"}

TRACE_STATUS_TO_MODE = {
    "actual-trace": "actual_subagent",
    "actual-trace-incomplete": "actual_subagent_incomplete",
    "fallback-stated": "sequential_fallback",
    "claim-without-reliable-trace": "false_actual_claim",
    "no-trace": "direct",
    "trace not captured": "trace_not_captured",
    "missing trace": "trace_missing",
    "skipped": "not_run",
}

KNOWN_MODES = set(TRACE_STATUS_TO_MODE.values()) | {"unknown"}


@dataclass(frozen=True)
class WorkflowExpectation:
    expected_mode: str
    acceptable_modes: tuple[str, ...]
    forbidden_modes: tuple[str, ...]
    report_label: str


@dataclass(frozen=True)
class GateResult:
    expected: WorkflowExpectation | None
    actual_mode: str
    alignment: str
    findings: list[str]


def block_lines(text: str, key: str) -> list[str]:
    match = re.search(rf"(?m)^(?P<indent>\s*){re.escape(key)}\s*:\s*(?:#.*)?\n", text)
    if not match:
        return []
    base_indent = len(match.group("indent"))
    lines: list[str] = []
    for line in text[match.end() :].splitlines():
        if (
            line.strip()
            and len(line) - len(line.lstrip()) <= base_indent
            and not line.lstrip().startswith("-")
        ):
            break
        if line.strip():
            lines.append(line.strip())
    return lines


def scalar_value(text: str, key: str) -> str:
    match = re.search(rf"(?m)^\s*{re.escape(key)}\s*:\s*(.*?)\s*(?:#.*)?$", text)
    if not match:
        return ""
    return match.group(1).strip().strip("'\"")


def yaml_list_values(text: str, key: str) -> list[str]:
    values: list[str] = []
    for line in block_lines(text, key):
        item = re.match(r"^-\s+(.+?)\s*$", line)
        if item:
            values.append(item.group(1).strip().strip("'\""))
    return [value for value in values if value]


def parse_workflow_expectation(answer_text: str) -> WorkflowExpectation | None:
    block = "\n".join(block_lines(answer_text, "workflow_execution_expectation"))
    if not block:
        return None
    return WorkflowExpectation(
        expected_mode=scalar_value(block, "expected_mode"),
        acceptable_modes=tuple(yaml_list_values(block, "acceptable_modes")),
        forbidden_modes=tuple(yaml_list_values(block, "forbidden_modes")),
        report_label=scalar_value(block, "report_label"),
    )


def actual_workflow_mode(trace: dict[str, Any]) -> str:
    status = str(trace.get("traceStatus") or "")
    return TRACE_STATUS_TO_MODE.get(status, "unknown")


def workflow_alignment(actual_mode: str, expectation: WorkflowExpectation | None) -> str:
    if expectation is None:
        return "n/a"
    if actual_mode in expectation.forbidden_modes:
        return "위반"
    if actual_mode in ALWAYS_HARD_FAIL_MODES:
        return "위반"
    if actual_mode in expectation.acceptable_modes:
        return "정상"
    return "위반"


def gate_findings(
    *,
    answer_text: str,
    trace: dict[str, Any],
    case_id: str,
    variant: str,
) -> GateResult:
    expectation = parse_workflow_expectation(answer_text)
    actual_mode = actual_workflow_mode(trace)
    if expectation is None:
        return GateResult(
            expected=None,
            actual_mode=actual_mode,
            alignment="n/a",
            findings=[],
        )

    findings: list[str] = []
    prefix = f"{case_id} {variant}: workflow execution mode {actual_mode}"
    if actual_mode in expectation.forbidden_modes:
        findings.append(f"{prefix} is forbidden by oracle")
    elif actual_mode not in expectation.acceptable_modes:
        findings.append(f"{prefix} is not in acceptable_modes")
    if actual_mode in ALWAYS_HARD_FAIL_MODES:
        findings.append(f"{prefix} is always a hard failure")

    return GateResult(
        expected=expectation,
        actual_mode=actual_mode,
        alignment=workflow_alignment(actual_mode, expectation),
        findings=findings,
    )
