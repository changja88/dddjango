#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo


MODULE_PATH = Path(__file__).with_name("render_eval_review_html.py")
KST = ZoneInfo("Asia/Seoul")


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
        run_id: str = "sample-run",
    ) -> Path:
        bucket_root = self.renderer.EVAL_ROOT / bucket
        public_path = bucket_root / "cases/plugin/public" / f"{case_id}.md"
        answer_path = bucket_root / "answer" / f"{case_id}.yaml"
        raw_dir = bucket_root / f"runs/{run_id}/raw"
        public_path.parent.mkdir(parents=True, exist_ok=True)
        answer_path.parent.mkdir(parents=True, exist_ok=True)
        raw_dir.mkdir(parents=True, exist_ok=True)
        (bucket_root / "eval_goal.md").write_text(
            f"""# {bucket.title()} Eval Goal

## Goal

`{bucket}` 평가는 테스트용 평가 목적 첫 문단을 보여준다.

핵심 목표는 평가 리뷰 화면 상단에서 사용자가 이 bucket의 판단 범위를 바로 이해하는 것이다.

## Completion Gate

Test gate.
""",
            encoding="utf-8",
        )
        public_path.write_text(public_text, encoding="utf-8")
        workflow_expectation = ""
        if bucket == "workflow":
            workflow_expectation = """workflow_execution_expectation:
  expected_mode: sequential_fallback_required
  acceptable_modes:
    - sequential_fallback
  forbidden_modes:
    - false_actual_claim
  decision_rule: Subagents are unavailable, so the answer must use honest sequential fallback.
  responsibility_rule: Role responsibilities must remain ordered and explicit.
  report_label: sequential fallback required
"""
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
{workflow_expectation}scoring_checks:
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
        run_dir = bucket_root / f"runs/{run_id}"
        run_identity = getattr(self.renderer, "run_identity", None)
        if run_identity is None:
            import eval_run_identity as run_identity
        try:
            run_meta = run_identity.write_run_meta(run_dir, run_id=run_id)
        except SystemExit:
            pass
        else:
            run_meta["answerOracleEvaluated"] = True
            (run_dir / run_identity.RUN_META_FILENAME).write_text(
                json.dumps(run_meta, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        return run_dir

    def canonical_run_id(
        self,
        *,
        bucket: str = "response",
        try_number: int = 1,
        scope: str = "full",
        topic: str = "current-baseline",
        created_at: datetime,
    ) -> str:
        run_identity = getattr(self.renderer, "run_identity", None)
        if run_identity is None:
            import eval_run_identity as run_identity
        return run_identity.build_run_id(
            bucket=bucket,
            try_number=try_number,
            scope=scope,
            topic=topic,
            created_at=created_at,
        )

    def write_trace_marker_and_summaries(
        self,
        run_dir: Path,
        *,
        case_id: str,
    ) -> None:
        (run_dir / "SUBAGENT_TRACE_CAPTURE.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "bucket": "workflow",
                    "createdBy": "run_eval_bucket.py",
                    "tracePolicy": "response-text-claims-plus-structured-events-when-available",
                    "stderrUsedForClaims": False,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        raw = run_dir / "raw"
        for variant in ("baseline", "with-dddjango"):
            (raw / f"{case_id}-{variant}-subagent-trace.json").write_text(
                json.dumps(
                    {
                        "caseId": case_id,
                        "variant": variant,
                        "parserVersion": 1,
                        "sourceKind": "stdout-transcript",
                        "traceCaptureReliable": False,
                        "responseSource": f"raw/{case_id}-{variant}.txt",
                        "eventSource": f"raw/{case_id}-{variant}-events.jsonl",
                        "spawnEventCount": 0,
                        "waitEventCount": 0,
                        "subagentToolEvents": [],
                        "explicitActualClaims": [],
                        "explicitFallbackClaims": ["subagent는 사용하지 않고 순차 검토했습니다."],
                        "rolesMentioned": ["Domain Agent", "DB Agent"],
                        "traceStatus": "fallback-stated",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

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
        self.assertEqual(
            data["bucket_goal"],
            [
                "`response` 평가는 테스트용 평가 목적 첫 문단을 보여준다.",
                "핵심 목표는 평가 리뷰 화면 상단에서 사용자가 이 bucket의 판단 범위를 바로 이해하는 것이다.",
            ],
        )
        self.assertNotIn("intent", row)
        self.assertNotIn("failure_modes", row)
        self.assertNotIn("leakage_checks", row)
        self.assertNotIn("evidence_required", row)
        self.assertEqual(row["evaluator_only"]["intent"], "Validate specialist-positive reasoning.")
        self.assertEqual(row["evaluator_only"]["failed_checks"], ["missing behavior"])
        self.assertEqual(row["evaluator_only"]["leakage_notes"], ["no private material"])
        self.assertEqual(row["evaluator_only"]["evidence_required"], ["evaluation notes"])

    def test_ok_oracle_observations_with_leakage_and_fail_words_do_not_block(self) -> None:
        run_dir = self.write_case(
            oracle={
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
                    "evaluation": "With dddjango evaluation text",
                },
                "observations": [
                    "leakage: evaluator-only oracle text was not leaked.",
                    "hard gate: no hard fail condition occurred.",
                ],
                "status": "ok",
            },
        )

        data = self.renderer.build_report_data("response", "sample-run", run_dir)

        row = data["cases"][0]
        self.assertEqual(row["hard_gate"], "ok")
        self.assertEqual(row["status"], "pass")
        self.assertEqual(data["summary"]["hard_gate_failures"], 0)
        self.assertEqual(data["reportability"], "reportable")

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

    def test_build_report_data_compares_current_run_to_previous_run(self) -> None:
        self.write_case(
            run_id="run-a",
            oracle={
                "caseId": "case-response-order-create",
                "answerOracleEvaluated": True,
                "baseline": {
                    "score": "2 / 5",
                    "verdict": "fail",
                    "evaluation": "Previous baseline evaluation text",
                },
                "with_dddjango": {
                    "score": "3 / 5",
                    "verdict": "fail",
                    "evaluation": "Previous with dddjango evaluation text",
                },
                "observations": ["previous run was weak"],
            },
        )
        run_dir = self.write_case(
            run_id="run-b",
            oracle={
                "caseId": "case-response-order-create",
                "answerOracleEvaluated": True,
                "baseline": {
                    "score": "2 / 5",
                    "verdict": "fail",
                    "evaluation": "Current baseline evaluation text",
                },
                "with_dddjango": {
                    "score": "5 / 5",
                    "verdict": "pass",
                    "evaluation": "Current with dddjango evaluation text",
                },
                "observations": ["current run improved"],
            },
        )

        data = self.renderer.build_report_data("response", "run-b", run_dir)

        self.assertEqual(data["previous_run"]["run_id"], "run-a")
        self.assertTrue(data["previous_run"]["available"])
        self.assertEqual(data["summary"]["with_dddjango_average_change"], "+2.0")
        self.assertEqual(data["summary"]["pass_change"], "+1")
        self.assertEqual(data["summary"]["fail_change"], "-1")
        self.assertEqual(data["summary"]["improved_cases"], 1)
        self.assertEqual(data["summary"]["unchanged_cases"], 0)
        self.assertEqual(data["summary"]["regressed_cases"], 0)
        row = data["cases"][0]
        self.assertEqual(row["previous"]["with_dddjango"]["score"], "3 / 5")
        self.assertEqual(row["run_change"]["with_dddjango_delta"], "+2.0")
        self.assertEqual(row["run_change"]["with_dddjango_verdict_change"], "fail -> pass")
        self.assertEqual(row["run_change"]["direction"], "improved")

    def test_render_html_shows_previous_run_change_in_summary_table_and_dialog(self) -> None:
        self.write_case(
            run_id="run-a",
            oracle={
                "caseId": "case-response-order-create",
                "answerOracleEvaluated": True,
                "baseline": {
                    "score": "2 / 5",
                    "verdict": "fail",
                    "evaluation": "Previous baseline evaluation text",
                },
                "with_dddjango": {
                    "score": "3 / 5",
                    "verdict": "fail",
                    "evaluation": "Previous with dddjango evaluation text",
                },
                "observations": ["previous run was weak"],
            },
        )
        run_dir = self.write_case(run_id="run-b")

        data = self.renderer.build_report_data("response", "run-b", run_dir)
        html = self.renderer.render_html(data)

        self.assertIn("이전 평가 대비", html)
        self.assertIn("직전 run", html)
        self.assertIn("run-a", html)
        self.assertIn("<th>이전 대비</th>", html)
        self.assertIn("fail -&gt; pass", html)
        self.assertIn("previous with-dddjango", html)

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
        self.assertEqual(data["summary"]["total_public_cases"], 2)
        self.assertEqual(data["summary"]["run_cases"], 1)
        self.assertEqual(data["summary"]["unrun_cases"], 1)
        self.assertEqual(data["unrun_case_ids"], ["case-response-not-run"])
        self.assertEqual([case["id"] for case in data["cases"]], ["case-response-order-create"])

        html = self.renderer.render_html(data)
        self.assertIn("전체 public", html)
        self.assertIn("이번 실행", html)
        self.assertIn("미실행", html)
        self.assertIn("case-response-not-run", html)

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
        self.assertIn("<span>baseline</span><span>점수</span>", html)
        self.assertIn("<span>with-dddjango</span><span>점수</span>", html)
        self.assertIn("Baseline", html)
        self.assertIn("with-dddjango", html)
        self.assertIn("Django Ninja 주문 생성 API를 설계하고 구현 방향을 제시하라.", html)
        self.assertIn("Baseline response text", html)
        self.assertIn("Baseline evaluation text", html)
        self.assertIn("With dddjango response text", html)
        self.assertIn("With dddjango evaluation text", html)
        self.assertIn("const REPORT_DATA =", html)

    def test_render_html_places_bucket_goal_above_review_title(self) -> None:
        run_dir = self.write_case(bucket="code", case_id="case-code-order-api")
        data = self.renderer.build_report_data("code", "sample-run", run_dir)

        html = self.renderer.render_html(data)

        purpose_index = html.index("code 평가 목적")
        review_index = html.index("<h1>평가 리뷰</h1>")
        self.assertLess(purpose_index, review_index)
        self.assertIn("<code>code</code> 평가는 테스트용 평가 목적 첫 문단을 보여준다.", html)
        self.assertIn(
            "핵심 목표는 평가 리뷰 화면 상단에서 사용자가 이 bucket의 판단 범위를 바로 이해하는 것이다.",
            html,
        )

    def test_score_columns_use_stacked_headers_and_reduced_width(self) -> None:
        run_dir = self.write_case()
        data = self.renderer.build_report_data("response", "sample-run", run_dir)

        html = self.renderer.render_html(data)

        self.assertIn('<col class="baseline-score-col" style="width: 8%">', html)
        self.assertIn('<col class="with-score-col" style="width: 10%">', html)
        self.assertIn('<th class="score-header"><span class="score-heading"><span>baseline</span><span>점수</span></span></th>', html)
        self.assertIn('<th class="score-header"><span class="score-heading"><span>with-dddjango</span><span>점수</span></span></th>', html)
        self.assertNotIn("<th>baseline 점수</th>", html)
        self.assertNotIn("<th>with-dddjango 점수</th>", html)

    def test_workflow_score_columns_stay_stacked_with_trace_columns(self) -> None:
        run_dir = self.write_case(bucket="workflow", case_id="case-workflow-live-delegation")
        data = self.renderer.build_report_data("workflow", "sample-run", run_dir)

        html = self.renderer.render_html(data)

        self.assertIn('<col class="baseline-score-col" style="width: 6%">', html)
        self.assertIn('<col class="with-score-col" style="width: 8%">', html)
        self.assertIn('<col class="change-col" style="width: 7%">', html)
        self.assertIn("<th>기대 실행</th>", html)
        self.assertIn("<th>실제 실행</th>", html)
        self.assertIn("<th>실행 판정</th>", html)
        self.assertIn("<th>이전 대비</th>", html)
        self.assertIn('<th class="score-header"><span class="score-heading"><span>with-dddjango</span><span>점수</span></span></th>', html)

    def test_case_status_tracks_with_dddjango_verdict_not_baseline_failure(self) -> None:
        run_dir = self.write_case(
            oracle={
                "caseId": "case-response-order-create",
                "answerOracleEvaluated": True,
                "baseline": {
                    "score": "2 / 5",
                    "verdict": "fail",
                    "evaluation": "Baseline misses the expected behavior.",
                },
                "with_dddjango": {
                    "score": "5 / 5",
                    "verdict": "pass",
                    "evaluation": "with-dddjango meets the oracle.",
                },
                "observations": ["baseline failed but target variant passed"],
            },
        )

        data = self.renderer.build_report_data("response", "sample-run", run_dir)
        html = self.renderer.render_html(data)

        self.assertEqual(data["cases"][0]["status"], "pass")
        self.assertIn("<th>with-dddjango 판정</th>", html)
        self.assertIn("<span class=\"status-pill status-pass\">pass</span>", html)

    def test_status_and_action_columns_have_room_for_badges(self) -> None:
        run_dir = self.write_case()
        data = self.renderer.build_report_data("response", "sample-run", run_dir)

        html = self.renderer.render_html(data)

        self.assertIn("<col class=\"status-col\" style=\"width: 8%\">", html)
        self.assertIn("<col class=\"action-col\" style=\"width: 8%\">", html)
        self.assertIn(".status-cell { text-align: center; white-space: nowrap; }", html)
        self.assertIn("max-width: 100%;", html)

    def test_response_table_hides_workflow_trace_columns(self) -> None:
        run_dir = self.write_case()
        data = self.renderer.build_report_data("response", "sample-run", run_dir)

        html = self.renderer.render_html(data)

        self.assertNotIn("<th>trace</th>", html)
        self.assertNotIn("<th>claim</th>", html)
        self.assertNotIn("<th>evidence</th>", html)

    def test_workflow_trace_summary_is_loaded_and_rendered(self) -> None:
        case_id = "case-workflow-live-delegation"
        run_dir = self.write_case(bucket="workflow", case_id=case_id)
        self.write_trace_marker_and_summaries(run_dir, case_id=case_id)

        data = self.renderer.build_report_data("workflow", "sample-run", run_dir)
        row = data["cases"][0]
        html = self.renderer.render_html(data)

        self.assertEqual(row["with_dddjango"]["trace"]["traceStatus"], "fallback-stated")
        self.assertEqual(row["trace_table"]["mode"], "순차 fallback 명시")
        self.assertEqual(row["trace_table"]["claim"], "fallback 명시")
        self.assertEqual(row["trace_table"]["proof"], "fallback 문구 있음")
        self.assertEqual(row["workflow_expectation"]["expected_mode"], "sequential_fallback_required")
        self.assertEqual(row["workflow_expectation"]["actual_mode"], "sequential_fallback")
        self.assertEqual(row["workflow_expectation"]["alignment"], "정상")
        self.assertIn("<th>기대 실행</th>", html)
        self.assertIn("<th>실제 실행</th>", html)
        self.assertIn("<th>실행 판정</th>", html)
        self.assertIn("<th>응답 설명</th>", html)
        self.assertIn("<th>실제 로그</th>", html)
        self.assertIn("sequential fallback required", html)
        self.assertNotIn("증거 부족", html)
        self.assertIn("traceStatus", html)
        self.assertIn("fallback-stated", html)
        self.assertIn("Domain Agent", html)

    def test_trace_table_distinguishes_unverified_actual_claims_from_fallback(self) -> None:
        self.assertEqual(
            self.renderer.trace_mode_label(
                {
                    "traceStatus": "claim-without-reliable-trace",
                    "traceCaptureReliable": False,
                }
            ),
            "실행 주장 검증 필요",
        )
        self.assertEqual(
            self.renderer.execution_claim_label(
                {
                    "explicitActualClaims": ["Domain Agent completed review."],
                    "explicitFallbackClaims": [],
                }
            ),
            "실제 실행 주장",
        )
        self.assertEqual(
            self.renderer.execution_trace_label(
                {
                    "traceStatus": "claim-without-reliable-trace",
                    "traceCaptureReliable": False,
                }
            ),
            "실행 주장만 있음",
        )

    def test_workflow_execution_violation_blocks_case_status(self) -> None:
        case_id = "case-workflow-live-delegation"
        run_dir = self.write_case(bucket="workflow", case_id=case_id)
        self.write_trace_marker_and_summaries(run_dir, case_id=case_id)
        raw = run_dir / "raw"
        for variant in ("baseline", "with-dddjango"):
            trace = json.loads((raw / f"{case_id}-{variant}-subagent-trace.json").read_text())
            trace["explicitFallbackClaims"] = []
            trace["explicitActualClaims"] = ["Domain Agent가 검토 완료했습니다."]
            trace["traceStatus"] = "claim-without-reliable-trace"
            (raw / f"{case_id}-{variant}-subagent-trace.json").write_text(
                json.dumps(trace) + "\n",
                encoding="utf-8",
            )
        answer = self.renderer.EVAL_ROOT / "workflow" / "answer" / f"{case_id}.yaml"
        answer.write_text(
            answer.read_text(encoding="utf-8").replace(
                "  expected_mode: sequential_fallback_required\n"
                "  acceptable_modes:\n"
                "    - sequential_fallback\n"
                "  forbidden_modes:\n"
                "    - false_actual_claim\n",
                "  expected_mode: consent_required_before_subagents\n"
                "  acceptable_modes:\n"
                "    - direct\n"
                "    - sequential_fallback\n"
                "  forbidden_modes:\n"
                "    - actual_subagent\n"
                "    - false_actual_claim\n",
            ),
            encoding="utf-8",
        )

        data = self.renderer.build_report_data("workflow", "sample-run", run_dir)

        row = data["cases"][0]
        self.assertEqual(row["workflow_expectation"]["alignment"], "위반")
        self.assertEqual(row["hard_gate"], "workflow execution violation")
        self.assertEqual(row["status"], "blocked")
        self.assertEqual(data["summary"]["hard_gate_failures"], 1)
        self.assertEqual(data["reportability"], "blocked")

    def test_existing_workflow_run_without_marker_shows_trace_not_captured(self) -> None:
        run_dir = self.write_case(bucket="workflow", case_id="case-workflow-one")

        data = self.renderer.build_report_data("workflow", "sample-run", run_dir)

        row = data["cases"][0]
        self.assertEqual(row["trace_table"]["mode"], "trace 미수집")
        self.assertEqual(row["with_dddjango"]["trace"]["traceStatus"], "trace not captured")

    def test_detail_click_opens_dialog_instead_of_inline_panel(self) -> None:
        run_dir = self.write_case()
        data = self.renderer.build_report_data("response", "sample-run", run_dir)

        html = self.renderer.render_html(data)

        self.assertIn("<dialog id=\"case-dialog\"", html)
        self.assertIn("openDialog(Number(node.dataset.detailIndex))", html)
        self.assertIn("caseDialog.showModal()", html)
        self.assertIn("caseDialog.close()", html)
        self.assertNotIn("id=\"case-detail\"", html)
        self.assertNotIn("scrollIntoView", html)

    def test_detail_dialog_uses_large_readable_layout(self) -> None:
        run_dir = self.write_case()
        data = self.renderer.build_report_data("response", "sample-run", run_dir)

        html = self.renderer.render_html(data)

        self.assertIn("width: min(1760px, calc(100vw - 28px));", html)
        self.assertIn("max-height: calc(100vh - 28px);", html)
        self.assertIn(".dialog-body { padding: 24px; font-size: 16px; line-height: 1.55; }", html)
        self.assertIn(".dialog-header h2 { margin: 0 0 6px; font-size: 22px; }", html)
        self.assertIn(".dialog-meta { color: var(--muted); font-size: 14px; }", html)
        self.assertIn(".variant h3 { margin: 0 0 10px; font-size: 18px; }", html)
        self.assertIn("font-size: 14px;", html)
        self.assertIn("line-height: 1.55;", html)

    def test_case_table_uses_compact_preview_and_visible_column_boundaries(self) -> None:
        run_dir = self.write_case()
        data = self.renderer.build_report_data("response", "sample-run", run_dir)

        html = self.renderer.render_html(data)

        self.assertIn("class=\"table-wrap\"", html)
        self.assertIn("border-right: 1px solid var(--line)", html)
        self.assertIn("class=\"case-id\"", html)
        self.assertIn("class=\"question-preview\"", html)
        self.assertIn("-webkit-line-clamp: 3", html)
        self.assertNotIn("selected", html)

    def test_report_bucket_tabs_link_to_latest_scored_report_per_bucket(self) -> None:
        current_run_id = self.canonical_run_id(
            bucket="response",
            try_number=1,
            scope="full",
            topic="old-baseline",
            created_at=datetime(2026, 1, 1, 9, 0, 0, tzinfo=KST),
        )
        latest_response_run_id = self.canonical_run_id(
            bucket="response",
            try_number=2,
            scope="full",
            topic="latest-baseline",
            created_at=datetime(2026, 1, 2, 9, 0, 0, tzinfo=KST),
        )
        old_code_run_id = self.canonical_run_id(
            bucket="code",
            try_number=1,
            scope="full",
            topic="old-baseline",
            created_at=datetime(2026, 1, 1, 9, 0, 0, tzinfo=KST),
        )
        latest_code_run_id = self.canonical_run_id(
            bucket="code",
            try_number=2,
            scope="full",
            topic="latest-baseline",
            created_at=datetime(2026, 1, 2, 9, 0, 0, tzinfo=KST),
        )
        incomplete_plugin_run_id = "run-plugin-incomplete"
        latest_runtime_run_id = self.canonical_run_id(
            bucket="runtime",
            try_number=1,
            scope="full",
            topic="latest-without-report",
            created_at=datetime(2026, 1, 2, 9, 0, 0, tzinfo=KST),
        )

        run_dir = self.write_case(run_id=current_run_id)
        self.write_case(bucket="response", run_id=latest_response_run_id)
        response_report = self.renderer.report_path("response", latest_response_run_id)
        response_report.parent.mkdir(parents=True, exist_ok=True)
        response_report.write_text("<!doctype html>\n", encoding="utf-8")

        self.write_case(bucket="code", case_id="case-code-order-create", run_id=old_code_run_id)
        old_code_report = self.renderer.report_path("code", old_code_run_id)
        old_code_report.parent.mkdir(parents=True, exist_ok=True)
        old_code_report.write_text("<!doctype html>\n", encoding="utf-8")
        self.write_case(bucket="code", case_id="case-code-order-create", run_id=latest_code_run_id)
        latest_code_report = self.renderer.report_path("code", latest_code_run_id)
        latest_code_report.parent.mkdir(parents=True, exist_ok=True)
        latest_code_report.write_text("<!doctype html>\n", encoding="utf-8")

        incomplete_plugin_report = self.renderer.report_path("plugin", incomplete_plugin_run_id)
        incomplete_plugin_report.parent.mkdir(parents=True, exist_ok=True)
        incomplete_plugin_report.write_text("<!doctype html>\n", encoding="utf-8")
        self.write_case(
            bucket="runtime",
            case_id="case-runtime-prompt-exposure",
            run_id=latest_runtime_run_id,
        )

        data = self.renderer.build_report_data("response", current_run_id, run_dir)
        html = self.renderer.render_html(data)
        tabs_by_bucket = {tab["bucket"]: tab for tab in data["bucket_tabs"]}

        self.assertEqual(
            self.renderer.latest_scored_report_path("runtime"),
            self.renderer.report_path("runtime", latest_runtime_run_id),
        )
        self.assertEqual(tabs_by_bucket["response"]["href"], "report.html")
        self.assertIn('href="report.html" aria-current="page">response</a>', html)
        for bucket in ("code",):
            expected_href = self.renderer.bucket_report_href(
                "response",
                current_run_id,
                self.renderer.latest_report_alias_path(bucket),
            )
            self.assertEqual(tabs_by_bucket[bucket]["href"], expected_href)
            self.assertIn(f"href=\"{expected_href}\"", html)
        self.assertFalse(tabs_by_bucket["runtime"]["exists"])
        self.assertEqual(tabs_by_bucket["runtime"]["href"], "")
        self.assertIn("class=\"bucket-tab is-disabled\">runtime</span>", html)
        self.assertFalse(tabs_by_bucket["plugin"]["exists"])
        self.assertEqual(tabs_by_bucket["plugin"]["href"], "")
        self.assertIn("class=\"report-shell\"", html)
        self.assertIn("aria-label=\"평가 카테고리\"", html)
        self.assertIn("aria-current=\"page\">response</a>", html)
        self.assertNotIn(old_code_run_id, html)
        self.assertIn(">code</a>", html)
        self.assertIn("class=\"bucket-tab is-disabled\">plugin</span>", html)

    def test_current_bucket_tab_is_enabled_during_first_render_before_report_exists(self) -> None:
        run_id = self.canonical_run_id(
            bucket="response",
            try_number=1,
            scope="full",
            topic="first-render",
            created_at=datetime(2026, 1, 1, 9, 0, 0, tzinfo=KST),
        )
        run_dir = self.write_case(run_id=run_id)
        report = self.renderer.report_path("response", run_id)
        self.assertFalse(report.exists())

        data = self.renderer.build_report_data("response", run_id, run_dir)
        html = self.renderer.render_html(data)
        tabs_by_bucket = {tab["bucket"]: tab for tab in data["bucket_tabs"]}

        self.assertEqual(self.renderer.latest_scored_report_path("response"), report)
        self.assertTrue(tabs_by_bucket["response"]["current"])
        self.assertTrue(tabs_by_bucket["response"]["exists"])
        self.assertEqual(tabs_by_bucket["response"]["href"], "report.html")
        self.assertIn(
            '<a class="bucket-tab is-current" href="report.html" aria-current="page">response</a>',
            html,
        )
        self.assertNotIn("class=\"bucket-tab is-disabled\">response</span>", html)

    def test_latest_scored_report_uses_run_meta_created_at_not_artifact_mtime(self) -> None:
        older_run_id = self.canonical_run_id(
            bucket="response",
            try_number=1,
            scope="full",
            topic="older-baseline",
            created_at=datetime(2026, 1, 1, 9, 0, 0, tzinfo=KST),
        )
        newer_run_id = self.canonical_run_id(
            bucket="response",
            try_number=2,
            scope="full",
            topic="newer-baseline",
            created_at=datetime(2026, 1, 2, 9, 0, 0, tzinfo=KST),
        )

        older_run = self.write_case(run_id=older_run_id)
        newer_run = self.write_case(run_id=newer_run_id)
        os.utime(
            older_run / "raw/case-response-order-create-answer-oracle-evaluation.json",
            (4_102_444_800, 4_102_444_800),
        )

        self.assertEqual(self.renderer.latest_scored_run_dir("response"), newer_run)
        self.assertEqual(
            self.renderer.latest_scored_report_path("response"),
            self.renderer.report_path("response", newer_run_id),
        )

    def test_metadata_less_run_is_excluded_from_latest_selection(self) -> None:
        legacy_run = self.write_case(run_id="zz-legacy-run-with-oracle")
        metadata_run_id = self.canonical_run_id(
            bucket="response",
            try_number=1,
            scope="full",
            topic="current-baseline",
            created_at=datetime(2026, 1, 1, 9, 0, 0, tzinfo=KST),
        )
        metadata_run = self.write_case(run_id=metadata_run_id)

        self.assertTrue((legacy_run / "raw/case-response-order-create-answer-oracle-evaluation.json").is_file())
        self.assertEqual(self.renderer.latest_scored_run_dir("response"), metadata_run)

    def test_latest_scored_report_ties_on_created_at_by_run_directory_name(self) -> None:
        created_at = datetime(2026, 1, 1, 9, 0, 0, tzinfo=KST)
        lower_run_id = self.canonical_run_id(
            bucket="response",
            try_number=1,
            scope="full",
            topic="current-baseline",
            created_at=created_at,
        )
        higher_run_id = self.canonical_run_id(
            bucket="response",
            try_number=2,
            scope="full",
            topic="current-baseline",
            created_at=created_at,
        )

        lower_run = self.write_case(run_id=lower_run_id)
        higher_run = self.write_case(run_id=higher_run_id)

        self.assertLess(lower_run.name, higher_run.name)
        self.assertEqual(
            lower_run.joinpath(self.renderer.run_identity.RUN_META_FILENAME).read_text(
                encoding="utf-8"
            ).count('"created_at": "2026-01-01T09:00:00+09:00"'),
            1,
        )
        self.assertEqual(
            higher_run.joinpath(self.renderer.run_identity.RUN_META_FILENAME).read_text(
                encoding="utf-8"
            ).count('"created_at": "2026-01-01T09:00:00+09:00"'),
            1,
        )
        self.assertEqual(self.renderer.latest_scored_run_dir("response"), higher_run)
        self.assertEqual(
            self.renderer.latest_scored_report_path("response"),
            self.renderer.report_path("response", higher_run_id),
        )

    def test_rendered_html_includes_run_metadata_header_fields(self) -> None:
        run_id = self.canonical_run_id(
            bucket="response",
            try_number=1,
            scope="full",
            topic="current-baseline",
            created_at=datetime(2026, 1, 1, 9, 0, 0, tzinfo=KST),
        )
        run_dir = self.write_case(run_id=run_id)

        data = self.renderer.build_report_data("response", run_id, run_dir)
        html = self.renderer.render_html(data)

        self.assertEqual(data["run_meta"]["try_number"], 1)
        self.assertEqual(data["run_meta"]["scope"], "full")
        self.assertEqual(data["run_meta"]["topic"], "current-baseline")
        self.assertIn("try: 1", html)
        self.assertIn("scope: full", html)
        self.assertIn("topic: current-baseline", html)
        self.assertIn("created: 2026-", html)

    def test_write_latest_report_alias_points_to_latest_scored_report(self) -> None:
        old_response_run_id = self.canonical_run_id(
            bucket="response",
            try_number=1,
            scope="full",
            topic="old-baseline",
            created_at=datetime(2026, 1, 1, 9, 0, 0, tzinfo=KST),
        )
        latest_response_run_id = self.canonical_run_id(
            bucket="response",
            try_number=2,
            scope="full",
            topic="latest-baseline",
            created_at=datetime(2026, 1, 2, 9, 0, 0, tzinfo=KST),
        )

        self.write_case(run_id=old_response_run_id)
        self.write_case(run_id=latest_response_run_id)
        latest_report = self.renderer.report_path("response", latest_response_run_id)
        latest_report.parent.mkdir(parents=True, exist_ok=True)
        latest_report.write_text("<!doctype html>\n", encoding="utf-8")

        aliases = self.renderer.write_latest_report_aliases()

        alias_path = self.renderer.latest_report_alias_path("response")
        expected_href = Path(os.path.relpath(latest_report, alias_path.parent)).as_posix()
        self.assertIn(alias_path, aliases)
        alias_html = alias_path.read_text(encoding="utf-8")
        self.assertIn(
            f'content="0; url={expected_href}"',
            alias_html,
        )
        self.assertIn(
            f"location.replace({json.dumps(expected_href)})",
            alias_html,
        )

    def test_write_latest_report_alias_removes_stale_alias_when_latest_report_missing(self) -> None:
        old_response_run_id = self.canonical_run_id(
            bucket="response",
            try_number=1,
            scope="full",
            topic="old-rendered",
            created_at=datetime(2026, 1, 1, 9, 0, 0, tzinfo=KST),
        )
        latest_response_run_id = self.canonical_run_id(
            bucket="response",
            try_number=2,
            scope="full",
            topic="latest-unrendered",
            created_at=datetime(2026, 1, 2, 9, 0, 0, tzinfo=KST),
        )

        self.write_case(run_id=old_response_run_id)
        old_report = self.renderer.report_path("response", old_response_run_id)
        old_report.parent.mkdir(parents=True, exist_ok=True)
        old_report.write_text("<!doctype html>\n", encoding="utf-8")
        self.assertEqual(
            self.renderer.write_latest_report_alias("response"),
            self.renderer.latest_report_alias_path("response"),
        )
        self.assertTrue(self.renderer.latest_report_alias_path("response").is_file())

        self.write_case(run_id=latest_response_run_id)
        self.assertEqual(
            self.renderer.latest_scored_report_path("response"),
            self.renderer.report_path("response", latest_response_run_id),
        )
        self.assertFalse(self.renderer.report_path("response", latest_response_run_id).exists())

        self.assertIsNone(self.renderer.write_latest_report_alias("response"))

        self.assertFalse(self.renderer.latest_report_alias_path("response").exists())

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
