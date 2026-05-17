#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("validate_eval_bucket_pack.py")


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_eval_bucket_pack", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EvalBucketPackValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = load_validator()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.validator.REPO_ROOT = self.root
        self.validator.EVAL_ROOT = self.root / "workspace/develop/eval"

    def write_case_pair(
        self,
        bucket: str,
        case_id: str,
        *,
        public_text: str = "사용자 요청처럼 작성된 공개 문제입니다.\n",
        coverage_tags: list[str] | None = None,
    ) -> None:
        public_path = (
            self.validator.EVAL_ROOT
            / bucket
            / "cases/plugin/public"
            / f"{case_id}.md"
        )
        answer_path = self.validator.EVAL_ROOT / bucket / "answer" / f"{case_id}.yaml"
        public_path.parent.mkdir(parents=True, exist_ok=True)
        answer_path.parent.mkdir(parents=True, exist_ok=True)
        public_path.write_text(public_text, encoding="utf-8")
        tags = coverage_tags if coverage_tags is not None else [case_id.removeprefix("case-")]
        tag_lines = "".join(f"  - {tag}\n" for tag in tags)
        answer_path.write_text(
            f"""id: {case_id}
case_id: {case_id}
bucket: {bucket}
kind: {bucket}
public_case: workspace/develop/eval/{bucket}/cases/plugin/public/{case_id}.md
intent: Validate one behavior.
reference_basis:
  - path: workspace/develop/eval/{bucket}/eval_goal.md
    basis: test basis
target_behavior:
  required:
    - Required behavior.
scoring_checks:
  - pass if checked.
hard_gates:
  - no evaluator-only material leaks.
failure_modes:
  - missing behavior
leakage_checks:
  - no private material
evidence_required:
  - evaluation notes
control_case: false
expected_outcomes:
  baseline: partial
  with_dddjango: pass
  expected_delta: positive
  baseline_pass_ok: false
coverage_tags:
{tag_lines}""",
            encoding="utf-8",
        )

    def test_public_case_rejects_oracle_schema_terms(self) -> None:
        public_path = self.root / "case.md"
        public_path.write_text(
            "reference_basis와 coverage_tags를 공개 문제에서 설명해줘.\n",
            encoding="utf-8",
        )

        findings = self.validator.validate_public_case(public_path)

        self.assertTrue(findings)

    def test_answer_rejects_empty_required_list_blocks(self) -> None:
        self.write_case_pair("source", "case-source-empty", coverage_tags=[])
        answer_path = self.validator.EVAL_ROOT / "source/answer/case-source-empty.yaml"
        public_path = (
            self.validator.EVAL_ROOT
            / "source/cases/plugin/public/case-source-empty.md"
        )

        findings = self.validator.validate_answer(answer_path, "source", public_path)

        self.assertTrue(any("coverage_tags" in finding for finding in findings))

    def test_answer_requires_expected_outcomes_and_hard_gates(self) -> None:
        self.write_case_pair("source", "case-source-quality")
        answer_path = self.validator.EVAL_ROOT / "source/answer/case-source-quality.yaml"
        text = answer_path.read_text(encoding="utf-8")
        text = text.replace("hard_gates:\n  - no evaluator-only material leaks.\n", "")
        text = text.replace(
            "expected_outcomes:\n"
            "  baseline: partial\n"
            "  with_dddjango: pass\n"
            "  expected_delta: positive\n"
            "  baseline_pass_ok: false\n",
            "",
        )
        answer_path.write_text(text, encoding="utf-8")
        public_path = (
            self.validator.EVAL_ROOT
            / "source/cases/plugin/public/case-source-quality.md"
        )

        findings = self.validator.validate_answer(answer_path, "source", public_path)

        self.assertTrue(any("missing hard_gates" in finding for finding in findings))
        self.assertTrue(any("missing expected_outcomes" in finding for finding in findings))

    def test_answer_requires_expected_outcome_fields(self) -> None:
        self.write_case_pair("source", "case-source-quality")
        answer_path = self.validator.EVAL_ROOT / "source/answer/case-source-quality.yaml"
        text = answer_path.read_text(encoding="utf-8")
        text = text.replace("  expected_delta: positive\n", "")
        public_path = (
            self.validator.EVAL_ROOT
            / "source/cases/plugin/public/case-source-quality.md"
        )
        answer_path.write_text(text, encoding="utf-8")

        findings = self.validator.validate_answer(answer_path, "source", public_path)

        self.assertTrue(any("expected_outcomes missing expected_delta" in finding for finding in findings))

    def test_answer_rejects_unknown_control_case_value(self) -> None:
        self.write_case_pair("source", "case-source-quality")
        answer_path = self.validator.EVAL_ROOT / "source/answer/case-source-quality.yaml"
        text = answer_path.read_text(encoding="utf-8").replace(
            "control_case: false",
            "control_case: maybe",
        )
        public_path = (
            self.validator.EVAL_ROOT
            / "source/cases/plugin/public/case-source-quality.md"
        )
        answer_path.write_text(text, encoding="utf-8")

        findings = self.validator.validate_answer(answer_path, "source", public_path)

        self.assertTrue(any("control_case must be one of" in finding for finding in findings))

    def test_bucket_requires_minimum_coverage_tags(self) -> None:
        self.write_case_pair(
            "response",
            "case-response-only-one",
            coverage_tags=["specialist-positive"],
        )

        _count, findings = self.validator.validate_bucket("response")

        self.assertTrue(any("coverage_tags" in finding for finding in findings))

    def test_workflow_answer_requires_execution_expectation(self) -> None:
        self.write_case_pair(
            "workflow",
            "case-workflow-one",
            coverage_tags=[
                "positive-composite",
                "review-focused",
                "handoff-contract",
                "risky-write-consistency",
                "role-map-sync",
                "delegation-honesty",
                "sequential-fallback",
                "subagent-opt-out",
                "tiny-task-restraint",
                "false-claim",
                "integration-closure",
            ],
        )
        answer_path = self.validator.EVAL_ROOT / "workflow/answer/case-workflow-one.yaml"
        public_path = (
            self.validator.EVAL_ROOT
            / "workflow/cases/plugin/public/case-workflow-one.md"
        )

        findings = self.validator.validate_answer(answer_path, "workflow", public_path)

        self.assertTrue(
            any("workflow_execution_expectation" in finding for finding in findings)
        )

    def test_workflow_execution_expectation_rejects_mode_overlap(self) -> None:
        path = self.root / "answer.yaml"
        text = """\
workflow_execution_expectation:
  expected_mode: sequential_fallback_required
  acceptable_modes:
    - sequential_fallback
  forbidden_modes:
    - sequential_fallback
  decision_rule: Use fallback.
  responsibility_rule: Preserve role order.
  report_label: fallback required
"""

        findings = self.validator.validate_workflow_execution_expectation(path, text)

        self.assertTrue(any("overlap" in finding for finding in findings))

    def test_workflow_execution_expectation_rejects_unknown_machine_modes(self) -> None:
        path = self.root / "answer.yaml"
        text = """\
workflow_execution_expectation:
  expected_mode: sequential_fallback_required
  acceptable_modes:
    - sequential_fallback
  forbidden_modes:
    - actual_subagent
    - wrong_order
  decision_rule: Use fallback.
  responsibility_rule: Preserve role order.
  report_label: fallback required
"""

        findings = self.validator.validate_workflow_execution_expectation(path, text)

        self.assertTrue(any("unknown machine mode" in finding for finding in findings))


if __name__ == "__main__":
    unittest.main()
