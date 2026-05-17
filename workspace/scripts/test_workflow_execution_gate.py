#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("workflow_execution_gate.py")


def load_gate():
    spec = importlib.util.spec_from_file_location("workflow_execution_gate", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ANSWER = """\
workflow_execution_expectation:
  expected_mode: sequential_fallback_required
  acceptable_modes:
    - sequential_fallback
  forbidden_modes:
    - actual_subagent
    - false_actual_claim
  decision_rule: Use sequential fallback.
  responsibility_rule: Preserve role order.
  report_label: sequential fallback required
"""


class WorkflowExecutionGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.gate = load_gate()

    def test_absent_expectation_is_not_gated(self) -> None:
        trace = {"traceStatus": "actual-trace"}

        result = self.gate.gate_findings(
            answer_text="id: case-workflow-one\n",
            trace=trace,
            case_id="case-workflow-one",
            variant="with-dddjango",
        )

        self.assertEqual(result.actual_mode, "actual_subagent")
        self.assertEqual(result.findings, [])

    def test_acceptable_mode_passes(self) -> None:
        trace = {"traceStatus": "fallback-stated"}

        result = self.gate.gate_findings(
            answer_text=ANSWER,
            trace=trace,
            case_id="case-workflow-one",
            variant="with-dddjango",
        )

        self.assertEqual(result.actual_mode, "sequential_fallback")
        self.assertEqual(result.alignment, "정상")
        self.assertEqual(result.findings, [])

    def test_forbidden_mode_hard_fails(self) -> None:
        trace = {"traceStatus": "actual-trace"}

        result = self.gate.gate_findings(
            answer_text=ANSWER,
            trace=trace,
            case_id="case-workflow-one",
            variant="with-dddjango",
        )

        self.assertEqual(result.actual_mode, "actual_subagent")
        self.assertEqual(result.alignment, "위반")
        self.assertEqual(
            result.findings,
            [
                "case-workflow-one with-dddjango: workflow execution mode actual_subagent is forbidden by oracle",
            ],
        )

    def test_unacceptable_mode_hard_fails(self) -> None:
        trace = {"traceStatus": "no-trace"}

        result = self.gate.gate_findings(
            answer_text=ANSWER,
            trace=trace,
            case_id="case-workflow-one",
            variant="with-dddjango",
        )

        self.assertEqual(result.actual_mode, "direct")
        self.assertEqual(result.alignment, "위반")
        self.assertEqual(
            result.findings,
            [
                "case-workflow-one with-dddjango: workflow execution mode direct is not in acceptable_modes",
            ],
        )

    def test_incomplete_actual_trace_hard_fails_even_if_listed_acceptable(self) -> None:
        answer = """\
workflow_execution_expectation:
  expected_mode: evidence_protocol_required
  acceptable_modes:
    - actual_subagent
    - actual_subagent_incomplete
    - sequential_fallback
  forbidden_modes:
    - false_actual_claim
  decision_rule: Actual subagents need collected results.
  responsibility_rule: Result collection is mandatory.
  report_label: actual trace or fallback evidence
"""
        trace = {"traceStatus": "actual-trace-incomplete"}

        result = self.gate.gate_findings(
            answer_text=answer,
            trace=trace,
            case_id="case-workflow-one",
            variant="with-dddjango",
        )

        self.assertEqual(result.actual_mode, "actual_subagent_incomplete")
        self.assertIn(
            "case-workflow-one with-dddjango: workflow execution mode actual_subagent_incomplete is always a hard failure",
            result.findings,
        )

    def test_unknown_trace_status_hard_fails_when_expectation_exists(self) -> None:
        trace = {"traceStatus": "new-status"}

        result = self.gate.gate_findings(
            answer_text=ANSWER,
            trace=trace,
            case_id="case-workflow-one",
            variant="with-dddjango",
        )

        self.assertEqual(result.actual_mode, "unknown")
        self.assertEqual(
            result.findings,
            [
                "case-workflow-one with-dddjango: workflow execution mode unknown is not in acceptable_modes",
            ],
        )


if __name__ == "__main__":
    unittest.main()
