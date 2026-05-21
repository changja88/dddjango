#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("validate_plan_constraints.py")


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_plan_constraints", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ValidatePlanConstraintsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = load_validator()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "repo"
        self.plan_root = self.root / "workspace/plan/skill_lv_up_plan"
        self.reference_plan_root = self.root / "workspace/plan/reference_lv_up_plan"
        self.eval_plan_root = self.root / "workspace/plan/eval_lv_up_plan"
        self.etc_plan_root = self.root / "workspace/plan/etc_lv_up_plan"
        self.reference_root = self.root / "workspace/reference"
        self.validator.REPO_ROOT = self.root
        self.validator.SKILL_LV_UP_PLAN_ROOT = self.plan_root
        self.validator.REFERENCE_LV_UP_PLAN_ROOT = self.reference_plan_root
        self.validator.EVAL_LV_UP_PLAN_ROOT = self.eval_plan_root
        self.validator.ETC_LV_UP_PLAN_ROOT = self.etc_plan_root
        self.validator.REFERENCE_ROOT = self.reference_root

    def test_missing_skill_lv_up_plan_root_is_valid(self) -> None:
        self.assertEqual(self.validator.validate_skill_lv_up_plan(self.plan_root), [])

    def test_valid_analysis_and_plan_files_pass(self) -> None:
        analysis = self.plan_root / "code/analysis/20260521-153012-try-01.md"
        analysis.parent.mkdir(parents=True)
        analysis.write_text("수정 대상: skill\n원인 분류: routing gap\n", encoding="utf-8")
        plan = self.plan_root / "code/plan/20260521-153012-try-01.md"
        plan.parent.mkdir(parents=True)
        plan.write_text("# 개선 계획\n", encoding="utf-8")

        self.assertEqual(self.validator.validate_skill_lv_up_plan(self.plan_root), [])

    def test_analysis_first_line_must_name_allowed_target(self) -> None:
        analysis = self.plan_root / "source/analysis/20260521-153012-try-01.md"
        analysis.parent.mkdir(parents=True)
        analysis.write_text("개선 대상: reference\n", encoding="utf-8")

        findings = self.validator.validate_skill_lv_up_plan(self.plan_root)

        self.assertEqual(len(findings), 1)
        self.assertIn("first line must start", findings[0])

    def test_unknown_bucket_and_section_fail(self) -> None:
        path = self.plan_root / "unknown/review/20260521-153012-try-01.md"
        path.parent.mkdir(parents=True)
        path.write_text("수정 대상: skill\n", encoding="utf-8")

        findings = self.validator.validate_skill_lv_up_plan(self.plan_root)

        self.assertEqual(len(findings), 1)
        self.assertIn("unknown bucket", findings[0])

    def test_unknown_section_fails_for_valid_bucket(self) -> None:
        path = self.plan_root / "workflow/review/20260521-153012-try-01.md"
        path.parent.mkdir(parents=True)
        path.write_text("수정 대상: skill\n", encoding="utf-8")

        findings = self.validator.validate_skill_lv_up_plan(self.plan_root)

        self.assertEqual(len(findings), 1)
        self.assertIn("unknown section", findings[0])

    def test_non_markdown_file_fails(self) -> None:
        path = self.plan_root / "runtime/plan/20260521-153012-try-01.txt"
        path.parent.mkdir(parents=True)
        path.write_text("plain text\n", encoding="utf-8")

        findings = self.validator.validate_skill_lv_up_plan(self.plan_root)

        self.assertEqual(len(findings), 1)
        self.assertIn("only .md files", findings[0])

    def test_generated_markdown_filename_must_start_with_timestamp(self) -> None:
        analysis = self.plan_root / "code/analysis/try-01.md"
        analysis.parent.mkdir(parents=True)
        analysis.write_text("수정 대상: skill\n", encoding="utf-8")

        findings = self.validator.validate_skill_lv_up_plan(self.plan_root)

        self.assertEqual(len(findings), 1)
        self.assertIn("filename must start with YYYYMMDD-HHMMSS-", findings[0])

    def test_nested_section_directory_fails(self) -> None:
        nested = self.plan_root / "code/analysis/nested"
        nested.mkdir(parents=True)
        (nested / "20260521-153012-try-01.md").write_text("수정 대상: skill\n", encoding="utf-8")

        findings = self.validator.validate_skill_lv_up_plan(self.plan_root)

        self.assertEqual(len(findings), 1)
        self.assertIn("nested directories are not allowed", findings[0])

    def test_plan_requires_matching_analysis_file(self) -> None:
        plan = self.plan_root / "code/plan/20260521-153012-try-01.md"
        plan.parent.mkdir(parents=True)
        plan.write_text("# 개선 계획\n", encoding="utf-8")

        findings = self.validator.validate_skill_lv_up_plan(self.plan_root)

        self.assertEqual(len(findings), 1)
        self.assertIn("matching analysis file is required", findings[0])

    def test_skill_plan_rejects_reference_target(self) -> None:
        analysis = self.plan_root / "code/analysis/20260521-153012-try-01.md"
        analysis.parent.mkdir(parents=True)
        analysis.write_text("수정 대상: reference\n", encoding="utf-8")

        findings = self.validator.validate_skill_lv_up_plan(self.plan_root)

        self.assertEqual(len(findings), 1)
        self.assertIn("not allowed here", findings[0])

    def test_reference_plan_uses_reference_area_and_reference_target(self) -> None:
        (self.reference_root / "architecture-ddd").mkdir(parents=True)
        analysis = self.reference_plan_root / "architecture-ddd/analysis/20260521-153012-try-01.md"
        analysis.parent.mkdir(parents=True)
        analysis.write_text("수정 대상: reference\n", encoding="utf-8")

        self.assertEqual(self.validator.validate_reference_lv_up_plan(self.reference_plan_root), [])

    def test_reference_plan_rejects_unknown_reference_area(self) -> None:
        (self.reference_root / "architecture-ddd").mkdir(parents=True)
        analysis = self.reference_plan_root / "unknown-area/analysis/20260521-153012-try-01.md"
        analysis.parent.mkdir(parents=True)
        analysis.write_text("수정 대상: reference\n", encoding="utf-8")

        findings = self.validator.validate_reference_lv_up_plan(self.reference_plan_root)

        self.assertEqual(len(findings), 1)
        self.assertIn("unknown reference area", findings[0])

    def test_eval_plan_allows_answer_target(self) -> None:
        analysis = self.eval_plan_root / "workflow/analysis/20260521-153012-try-01.md"
        analysis.parent.mkdir(parents=True)
        analysis.write_text("수정 대상: answer\n", encoding="utf-8")

        self.assertEqual(self.validator.validate_eval_lv_up_plan(self.eval_plan_root), [])

    def test_eval_plan_rejects_skill_target(self) -> None:
        analysis = self.eval_plan_root / "workflow/analysis/20260521-153012-try-01.md"
        analysis.parent.mkdir(parents=True)
        analysis.write_text("수정 대상: skill\n", encoding="utf-8")

        findings = self.validator.validate_eval_lv_up_plan(self.eval_plan_root)

        self.assertEqual(len(findings), 1)
        self.assertIn("not allowed here", findings[0])

    def test_etc_plan_uses_topic_name_and_process_target(self) -> None:
        analysis = self.etc_plan_root / "cleanup-process/analysis/20260521-153012-try-01.md"
        analysis.parent.mkdir(parents=True)
        analysis.write_text("수정 대상: process\n", encoding="utf-8")

        self.assertEqual(self.validator.validate_etc_lv_up_plan(self.etc_plan_root), [])

    def test_etc_plan_rejects_invalid_topic_name(self) -> None:
        analysis = self.etc_plan_root / "Cleanup Process/analysis/20260521-153012-try-01.md"
        analysis.parent.mkdir(parents=True)
        analysis.write_text("수정 대상: process\n", encoding="utf-8")

        findings = self.validator.validate_etc_lv_up_plan(self.etc_plan_root)

        self.assertEqual(len(findings), 1)
        self.assertIn("topic must use", findings[0])


if __name__ == "__main__":
    unittest.main()
