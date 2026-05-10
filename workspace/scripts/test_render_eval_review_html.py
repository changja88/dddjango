#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).with_name("render_eval_review_html.py")


def load_renderer():
    scripts_dir = str(MODULE_PATH.parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    spec = importlib.util.spec_from_file_location("render_eval_review_html", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EvalReviewHtmlRendererTests(unittest.TestCase):
    def setUp(self) -> None:
        self.renderer = load_renderer()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.renderer.REPO_ROOT = self.root
        self.renderer.EVAL_ROOT = self.root / "workspace/develop/eval"

    def write_case(
        self,
        *,
        bucket: str = "response",
        case_id: str = "case-response-order-create",
        public_text: str = "Django Ninja 주문 생성 API를 설계하고 구현 방향을 제시하라.\n",
        baseline_response: str | None = "Baseline response text",
        with_response: str | None = "With dddjango response text",
        oracle: dict[str, object] | None = None,
        oracle_text: str | None = None,
    ) -> Path:
        bucket_root = self.renderer.EVAL_ROOT / bucket
        public_path = bucket_root / "cases/plugin/public" / f"{case_id}.md"
        answer_path = bucket_root / "answer" / f"{case_id}.yaml"
        raw_dir = bucket_root / "runs/sample-run/raw"
        public_path.parent.mkdir(parents=True, exist_ok=True)
        answer_path.parent.mkdir(parents=True, exist_ok=True)
        raw_dir.mkdir(parents=True, exist_ok=True)
        public_path.write_text(public_text, encoding="utf-8")
        answer_path.write_text(
            f"""id: {case_id}
case_id: {case_id}
bucket: {bucket}
kind: {bucket}
public_case: workspace/develop/eval/{bucket}/cases/plugin/public/{case_id}.md
intent: Validate specialist-positive reasoning.
reference_basis:
  - path: workspace/develop/eval/{bucket}/eval_goal.md
    basis: test basis
target_behavior:
  required:
    - Required behavior.
scoring_checks:
  - pass if checked.
failure_modes:
  - missing behavior
leakage_checks:
  - no private material
evidence_required:
  - evaluation notes
coverage_tags:
  - specialist-positive
""",
            encoding="utf-8",
        )
        if baseline_response is not None:
            (raw_dir / f"{case_id}-baseline.txt").write_text(baseline_response, encoding="utf-8")
        if with_response is not None:
            (raw_dir / f"{case_id}-with-dddjango.txt").write_text(with_response, encoding="utf-8")
        if oracle is None and oracle_text is None:
            oracle = {
                "caseId": case_id,
                "answerOracleEvaluated": True,
                "baseline": {
                    "score": "2 / 5",
                    "verdict": "fail",
                    "evaluation_summary": "Missing dddjango-specific API and idempotency guidance.",
                    "evaluation": "Baseline evaluation text",
                },
                "with_dddjango": {
                    "score": "5 / 5",
                    "verdict": "pass",
                    "evaluation_summary": "Meets DDD, API, DB, and test expectations.",
                    "evaluation": "With dddjango evaluation text",
                },
                "observations": ["with-dddjango improves the response"],
            }
        if oracle_text is not None:
            (raw_dir / f"{case_id}-answer-oracle-evaluation.json").write_text(
                oracle_text,
                encoding="utf-8",
            )
        elif oracle is not None:
            (raw_dir / f"{case_id}-answer-oracle-evaluation.json").write_text(
                json.dumps(oracle, ensure_ascii=False),
                encoding="utf-8",
            )
        return bucket_root / "runs/sample-run"

    def test_build_report_data_includes_summary_rows_and_detail(self) -> None:
        run_dir = self.write_case()

        data = self.renderer.build_report_data("response", "sample-run", run_dir)

        self.assertEqual(data["summary"]["total_cases"], 1)
        self.assertEqual(data["summary"]["baseline_average"], "2.0")
        self.assertEqual(data["summary"]["with_dddjango_average"], "5.0")
        self.assertEqual(data["summary"]["delta"], "+3.0")
        row = data["cases"][0]
        self.assertEqual(row["question"], "Django Ninja 주문 생성 API를 설계하고 구현 방향을 제시하라.")
        self.assertEqual(row["baseline"]["score"], "2 / 5")
        self.assertEqual(row["with_dddjango"]["score"], "5 / 5")
        self.assertEqual(row["baseline"]["response"], "Baseline response text")
        self.assertEqual(row["baseline"]["evaluation"], "Baseline evaluation text")
        self.assertEqual(row["with_dddjango"]["response"], "With dddjango response text")
        self.assertEqual(row["with_dddjango"]["evaluation"], "With dddjango evaluation text")
        self.assertNotIn("intent", row)
        self.assertNotIn("failure_modes", row)
        self.assertNotIn("leakage_checks", row)
        self.assertNotIn("evidence_required", row)
        self.assertEqual(row["evaluator_only"]["intent"], "Validate specialist-positive reasoning.")
        self.assertEqual(row["evaluator_only"]["failed_checks"], ["missing behavior"])
        self.assertEqual(row["evaluator_only"]["leakage_notes"], ["no private material"])
        self.assertEqual(row["evaluator_only"]["evidence_required"], ["evaluation notes"])

    def test_summary_delta_uses_only_paired_scored_cases(self) -> None:
        self.write_case()
        run_dir = self.write_case(
            case_id="case-response-with-only-score",
            public_text="Second case with no baseline artifact.\n",
            baseline_response=None,
            oracle={
                "caseId": "case-response-with-only-score",
                "answerOracleEvaluated": True,
                "baseline": {
                    "score": "4 / 5",
                    "verdict": "pass",
                    "evaluation": "Baseline evaluation text",
                },
                "with_dddjango": {
                    "score": "1 / 5",
                    "verdict": "fail",
                    "evaluation": "With dddjango evaluation text",
                },
                "observations": ["baseline artifact missing"],
            },
        )

        data = self.renderer.build_report_data("response", "sample-run", run_dir)

        self.assertEqual(data["summary"]["total_cases"], 2)
        self.assertEqual(data["summary"]["baseline_average"], "2.0")
        self.assertEqual(data["summary"]["with_dddjango_average"], "3.0")
        self.assertEqual(data["summary"]["delta"], "+3.0")

    def test_report_includes_only_cases_present_in_run_artifacts(self) -> None:
        run_dir = self.write_case()
        extra_public_path = (
            self.renderer.EVAL_ROOT
            / "response/cases/plugin/public/case-response-not-run.md"
        )
        extra_answer_path = self.renderer.EVAL_ROOT / "response/answer/case-response-not-run.yaml"
        extra_public_path.write_text("This case was not part of the run.\n", encoding="utf-8")
        extra_answer_path.write_text(
            """id: case-response-not-run
case_id: case-response-not-run
bucket: response
kind: response
public_case: workspace/develop/eval/response/cases/plugin/public/case-response-not-run.md
intent: Not run.
reference_basis:
  - path: workspace/develop/eval/response/eval_goal.md
    basis: test basis
target_behavior:
  required:
    - Not run.
scoring_checks:
  - not run.
failure_modes:
  - not run
leakage_checks:
  - no private material
evidence_required:
  - evaluation notes
coverage_tags:
  - not-run
""",
            encoding="utf-8",
        )

        data = self.renderer.build_report_data("response", "sample-run", run_dir)

        self.assertEqual(data["summary"]["total_cases"], 1)
        self.assertEqual([case["id"] for case in data["cases"]], ["case-response-order-create"])

    def test_missing_artifacts_are_unscored_not_pass(self) -> None:
        run_dir = self.write_case(baseline_response=None, oracle={})

        data = self.renderer.build_report_data("response", "sample-run", run_dir)

        row = data["cases"][0]
        self.assertEqual(row["baseline"]["verdict"], "unscored")
        self.assertEqual(row["baseline"]["score"], "not scored")
        self.assertIn(row["status"], {"blocked", "unscored"})
        self.assertGreaterEqual(data["summary"]["missing_or_weak_evidence"], 1)

    def test_invalid_oracle_json_blocks_case(self) -> None:
        run_dir = self.write_case(oracle_text='{"answerOracleEvaluated": true,')

        data = self.renderer.build_report_data("response", "sample-run", run_dir)

        row = data["cases"][0]
        self.assertEqual(row["detail_status"], "invalid oracle json")
        self.assertEqual(row["status"], "unscored")
        self.assertEqual(row["baseline"]["verdict"], "unscored")
        self.assertEqual(row["with_dddjango"]["verdict"], "unscored")
        self.assertEqual(row["baseline"]["score"], "not scored")
        self.assertEqual(row["with_dddjango"]["score"], "not scored")

    def test_score_without_evaluation_is_not_scored_and_unscored(self) -> None:
        run_dir = self.write_case(
            oracle={
                "caseId": "case-response-order-create",
                "answerOracleEvaluated": True,
                "baseline": {
                    "score": "4 / 5",
                    "verdict": "pass",
                },
                "with_dddjango": {
                    "score": "5 / 5",
                    "verdict": "pass",
                    "evaluation": "With dddjango evaluation text",
                },
                "observations": ["baseline evaluation missing"],
            },
        )

        data = self.renderer.build_report_data("response", "sample-run", run_dir)

        row = data["cases"][0]
        self.assertEqual(row["status"], "unscored")
        self.assertEqual(row["baseline"]["verdict"], "unscored")
        self.assertEqual(row["baseline"]["score"], "not scored")
        self.assertIsNone(row["baseline"]["score_value"])

    def test_non_object_oracle_json_is_invalid_schema(self) -> None:
        run_dir = self.write_case(oracle_text='["not", "an", "object"]')

        data = self.renderer.build_report_data("response", "sample-run", run_dir)

        row = data["cases"][0]
        self.assertEqual(row["detail_status"], "invalid oracle schema")
        self.assertEqual(row["status"], "unscored")

    def test_oracle_case_id_mismatch_is_invalid_schema_and_unscored(self) -> None:
        run_dir = self.write_case(
            oracle={
                "caseId": "case-response-other",
                "answerOracleEvaluated": True,
                "baseline": {
                    "score": "4 / 5",
                    "verdict": "pass",
                    "evaluation": "Baseline evaluation text",
                },
                "with_dddjango": {
                    "score": "5 / 5",
                    "verdict": "pass",
                    "evaluation": "With dddjango evaluation text",
                },
                "observations": ["case id mismatch must block scoring"],
            },
        )

        data = self.renderer.build_report_data("response", "sample-run", run_dir)

        row = data["cases"][0]
        self.assertEqual(row["detail_status"], "invalid oracle schema")
        self.assertEqual(row["status"], "unscored")
        self.assertEqual(row["baseline"]["verdict"], "unscored")
        self.assertEqual(row["with_dddjango"]["verdict"], "unscored")
        self.assertEqual(row["baseline"]["score"], "not scored")
        self.assertEqual(row["with_dddjango"]["score"], "not scored")

    def test_missing_variant_schema_is_invalid_schema_and_unscored(self) -> None:
        cases = (
            (
                "missing with evaluation",
                {
                    "caseId": "case-response-order-create",
                    "answerOracleEvaluated": True,
                    "baseline": {
                        "score": "4 / 5",
                        "verdict": "pass",
                        "evaluation": "Baseline evaluation text",
                    },
                    "with_dddjango": {
                        "score": "5 / 5",
                        "verdict": "pass",
                    },
                    "observations": ["with-dddjango evaluation missing"],
                },
            ),
            (
                "missing with variant",
                {
                    "caseId": "case-response-order-create",
                    "answerOracleEvaluated": True,
                    "baseline": {
                        "score": "4 / 5",
                        "verdict": "pass",
                        "evaluation": "Baseline evaluation text",
                    },
                    "observations": ["with-dddjango object missing"],
                },
            ),
        )
        for label, oracle in cases:
            with self.subTest(label=label):
                run_dir = self.write_case(oracle=oracle)

                data = self.renderer.build_report_data("response", "sample-run", run_dir)

                row = data["cases"][0]
                self.assertEqual(row["detail_status"], "invalid oracle schema")
                self.assertEqual(row["status"], "unscored")
                self.assertEqual(row["baseline"]["verdict"], "unscored")
                self.assertEqual(row["with_dddjango"]["verdict"], "unscored")
                self.assertEqual(row["baseline"]["score"], "not scored")
                self.assertEqual(row["with_dddjango"]["score"], "not scored")

    def test_evaluation_summary_only_oracle_is_ready_and_populates_evaluation(self) -> None:
        run_dir = self.write_case(
            oracle={
                "caseId": "case-response-order-create",
                "answerOracleEvaluated": True,
                "baseline": {
                    "score": "3 / 5",
                    "verdict": "partial",
                    "evaluation_summary": "Baseline summary-only evaluation.",
                },
                "with_dddjango": {
                    "score": "5 / 5",
                    "verdict": "pass",
                    "evaluation_summary": "With summary-only evaluation.",
                },
                "observations": ["summary-only oracle is valid"],
            },
        )

        data = self.renderer.build_report_data("response", "sample-run", run_dir)

        row = data["cases"][0]
        self.assertEqual(row["detail_status"], "ready")
        self.assertEqual(row["baseline"]["evaluation"], "Baseline summary-only evaluation.")
        self.assertEqual(row["with_dddjango"]["evaluation"], "With summary-only evaluation.")
        self.assertEqual(row["baseline"]["score"], "3 / 5")
        self.assertEqual(row["with_dddjango"]["score"], "5 / 5")

    def test_main_rejects_missing_run_dir_even_with_temp_output(self) -> None:
        output = self.root / "tmp-report.html"
        argv = [
            "render_eval_review_html.py",
            "--bucket",
            "response",
            "--run-id",
            "missing-run",
            "--output",
            str(output),
        ]

        with patch.object(sys, "argv", argv):
            with self.assertRaises(SystemExit) as raised:
                self.renderer.main()

        self.assertIn("run directory does not exist", str(raised.exception))
        self.assertFalse(output.exists())

    def test_render_html_escapes_hostile_payloads(self) -> None:
        hostile = """## User Request
```text
</script><script>alert("x")</script><img src=x onerror=alert(1)> '" &
```
"""
        run_dir = self.write_case(
            public_text=hostile,
            baseline_response='baseline </script><script>alert("b")</script><img src=x onerror=alert(1)>',
            with_response='with </script><script>alert("w")</script><img src=x onerror=alert(1)>',
            oracle={
                "caseId": "case-response-order-create",
                "answerOracleEvaluated": True,
                "baseline": {
                    "score": "1 / 5",
                    "verdict": "fail",
                    "evaluation": 'eval </script><script>alert("e")</script><img src=x onerror=alert(1)>',
                },
                "with_dddjango": {
                    "score": "5 / 5",
                    "verdict": "pass",
                    "evaluation": 'eval2 </script><script>alert("e2")</script><img src=x onerror=alert(1)>',
                },
                "observations": ['obs </script><script>alert("o")</script>'],
            },
        )

        data = self.renderer.build_report_data("response", "sample-run", run_dir)
        html = self.renderer.render_html(data)

        report_start = html.index("const REPORT_DATA =")
        report_script = html[report_start : html.index("</script>", report_start)]
        self.assertIn("<\\/script>", report_script)
        self.assertNotIn("</script><script>", report_script)
        self.assertNotIn("<img src=x onerror=alert(1)>", html)
        self.assertIn("&lt;img", html)

    def test_render_html_contains_required_review_surfaces(self) -> None:
        run_dir = self.write_case()
        data = self.renderer.build_report_data("response", "sample-run", run_dir)

        html = self.renderer.render_html(data)

        self.assertIn("평가 요약", html)
        self.assertIn("평가 질문", html)
        self.assertIn("baseline 점수", html)
        self.assertIn("with-dddjango 점수", html)
        self.assertIn("Baseline", html)
        self.assertIn("with-dddjango", html)
        self.assertIn("Django Ninja 주문 생성 API를 설계하고 구현 방향을 제시하라.", html)
        self.assertIn("Baseline response text", html)
        self.assertIn("Baseline evaluation text", html)
        self.assertIn("With dddjango response text", html)
        self.assertIn("With dddjango evaluation text", html)
        self.assertIn("const REPORT_DATA =", html)

    def test_detail_click_scrolls_detail_panel_into_view(self) -> None:
        run_dir = self.write_case()
        data = self.renderer.build_report_data("response", "sample-run", run_dir)

        html = self.renderer.render_html(data)

        self.assertIn("scrollIntoView", html)
        self.assertIn("selectCase(Number(node.dataset.caseIndex), { scroll: true })", html)

    def test_public_case_text_is_not_modified_by_report_build_or_render(self) -> None:
        run_dir = self.write_case()
        public_path = (
            self.renderer.EVAL_ROOT
            / "response/cases/plugin/public/case-response-order-create.md"
        )
        before = public_path.read_text(encoding="utf-8")

        data = self.renderer.build_report_data("response", "sample-run", run_dir)
        self.renderer.render_html(data)

        self.assertEqual(public_path.read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main()
