#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("eval_run_common.py")


def load_common():
    spec = importlib.util.spec_from_file_location("eval_run_common", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class EvalRunCommonTests(unittest.TestCase):
    def setUp(self) -> None:
        self.common = load_common()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.common.REPO_ROOT = self.root
        self.common.EVAL_ROOT = self.root / "workspace/develop/eval"

    def write_case(self, bucket: str, case_id: str) -> Path:
        path = self.common.EVAL_ROOT / bucket / "cases/plugin/public" / f"{case_id}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("사용자 요청입니다.\n", encoding="utf-8")
        return path

    def valid_oracle(self, case_id: str = "case-example") -> dict[str, object]:
        return {
            "caseId": case_id,
            "answerOracleEvaluated": True,
            "baseline": {
                "score": "2 / 5",
                "verdict": "fail",
                "evaluation_summary": "baseline weak",
            },
            "with_dddjango": {
                "score": "5 / 5",
                "verdict": "pass",
                "evaluation_summary": "with-dddjango strong",
            },
            "observations": ["clear delta"],
        }

    def test_bucket_paths_use_existing_namespace(self) -> None:
        paths = self.common.bucket_paths("workflow")

        self.assertEqual(
            paths.public_cases_dir,
            self.common.EVAL_ROOT / "workflow/cases/plugin/public",
        )
        self.assertEqual(paths.answer_dir, self.common.EVAL_ROOT / "workflow/answer")
        self.assertEqual(paths.runs_dir, self.common.EVAL_ROOT / "workflow/runs")

    def test_selected_case_paths_reject_unknown_case(self) -> None:
        self.write_case("response", "case-response-one")

        with self.assertRaisesRegex(SystemExit, "Unknown case"):
            self.common.selected_case_paths("response", ["case-response-missing"])

    def test_extract_json_object_accepts_fenced_json(self) -> None:
        text = 'Here is the result:\n```json\n{"caseId": "case-a"}\n```'

        value = self.common.extract_json_object(text)

        self.assertEqual(value, {"caseId": "case-a"})

    def test_extract_json_object_accepts_embedded_non_fenced_json(self) -> None:
        text = 'prefix {"caseId": "case-a"} suffix'

        value = self.common.extract_json_object(text)

        self.assertEqual(value, {"caseId": "case-a"})

    def test_extract_json_object_raises_when_no_json_object_parses(self) -> None:
        with self.assertRaisesRegex(ValueError, "no JSON object found"):
            self.common.extract_json_object("[]")

    def test_validate_oracle_schema_requires_both_variants(self) -> None:
        error = self.common.validate_oracle_schema(
            {
                "caseId": "case-a",
                "answerOracleEvaluated": True,
                "baseline": {
                    "score": "4 / 5",
                    "verdict": "pass",
                    "evaluation": "baseline ok",
                },
                "observations": ["with-dddjango missing"],
            },
            "case-a",
        )

        self.assertEqual(error, "with_dddjango must be an object")

    def test_validate_oracle_schema_accepts_summary_field(self) -> None:
        error = self.common.validate_oracle_schema(
            {
                "caseId": "case-a",
                "answerOracleEvaluated": True,
                "baseline": {
                    "score": "2 / 5",
                    "verdict": "fail",
                    "evaluation_summary": "baseline weak",
                },
                "with_dddjango": {
                    "score": "5 / 5",
                    "verdict": "pass",
                    "evaluation_summary": "with-dddjango strong",
                },
                "observations": ["clear delta"],
            },
            "case-a",
        )

        self.assertIsNone(error)

    def test_validate_oracle_schema_rejects_unknown_verdict(self) -> None:
        oracle = self.valid_oracle()
        oracle["with_dddjango"]["verdict"] = "great"  # type: ignore[index]

        error = self.common.validate_oracle_schema(oracle, "case-example")

        self.assertEqual(error, "with_dddjango.verdict is unsupported: great")

    def test_validate_oracle_schema_rejects_out_of_range_score(self) -> None:
        oracle = self.valid_oracle()
        oracle["with_dddjango"]["score"] = "6 / 5"  # type: ignore[index]

        error = self.common.validate_oracle_schema(oracle, "case-example")

        self.assertEqual(error, "with_dddjango.score must be between 0 and 5")


if __name__ == "__main__":
    unittest.main()
