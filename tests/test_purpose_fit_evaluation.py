import json
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "evals/dddjango/scripts"
sys.path.insert(0, str(SCRIPTS))

import render_report  # noqa: E402
import run_evaluation  # noqa: E402
import run_calibration  # noqa: E402
import score_outputs  # noqa: E402
import validate_eval_config  # noqa: E402
from eval_lib import latest_run_dir, load_cases, load_dimensions, load_gates, load_reference_matrix, read_json  # noqa: E402


class PurposeFitConfigTests(unittest.TestCase):
    def test_eval_config_is_valid(self):
        validate_eval_config.validate_all()

    def test_core_policy_cases_have_baselines_and_dimensions(self):
        dimensions = load_dimensions()
        cases = load_cases("core-policy")

        self.assertEqual(len(cases), 5)
        for case in cases:
            with self.subTest(case=case["id"]):
                self.assertTrue((ROOT / "evals/dddjango" / case["baseline"]).exists())
                for dimension in case["required_dimensions"]:
                    self.assertIn(dimension, dimensions)

    def test_purpose_fit_suites_cover_plugin_goals(self):
        cases = load_cases()
        suites = {case["suite"] for case in cases}
        case_ids = {case["id"] for case in cases}

        self.assertIn("core-policy", suites)
        self.assertIn("review-refactor", suites)
        self.assertIn("trigger-usability", suites)
        self.assertIn("subagent-workflow", suites)
        self.assertIn("reference-maximum", suites)
        self.assertIn("holdout-adversarial", suites)
        self.assertIn("code-structure", suites)
        self.assertIn("r01-fat-model-review", case_ids)
        self.assertIn("t02-fastapi-no-contamination", case_ids)
        self.assertIn("t05-django-template-view", case_ids)
        self.assertIn("t06-flask-no-contamination", case_ids)
        self.assertIn("s01-order-feature-role-map", case_ids)
        self.assertIn("m01-ninja-error-standard", case_ids)
        self.assertIn("m03-ninja-list-filter-pagination", case_ids)
        self.assertIn("m04-db-transaction-idempotency", case_ids)
        self.assertIn("m05-tdd-edge-cases", case_ids)
        self.assertIn("h01-drf-before-after-migration", case_ids)
        self.assertIn("h02-keyword-bait-order-design", case_ids)
        self.assertIn("h03-starlette-no-contamination", case_ids)
        self.assertIn("s02-simple-no-delegation", case_ids)
        self.assertIn("s03-parallel-safe-review", case_ids)
        self.assertIn("s04-same-file-conflict-sequential", case_ids)
        self.assertIn("s05-false-subagent-claim", case_ids)
        self.assertIn("s06-integration-conflict-resolution", case_ids)
        self.assertIn("p01-order-feature-file-tree", case_ids)
        self.assertIn("p02-domain-code-quality", case_ids)

    def test_core_policy_does_not_require_single_implementation_preference(self):
        cases = {case["id"]: case for case in load_cases("core-policy")}

        self.assertNotIn("@dataclass", cases["c03-tdd-coupon-policy"]["required_patterns"])
        self.assertNotIn("select_for_update", cases["c05-inventory-reservation"]["required_patterns"])
        group_labels = {
            group["label"]
            for group in cases["c05-inventory-reservation"]["alternative_pattern_groups"]
        }
        self.assertIn("concurrency_control", group_labels)

    def test_reference_matrix_covers_all_cases(self):
        cases = {case["id"]: case for case in load_cases()}
        matrix = load_reference_matrix()["cases"]

        self.assertEqual(set(matrix), set(cases))
        for case_id, case in cases.items():
            with self.subTest(case=case_id):
                self.assertEqual(matrix[case_id]["expected_skills"], case["expected_skills"])
                for path in matrix[case_id].get("reference_paths", []):
                    self.assertTrue((ROOT / path).exists())
                for path in matrix[case_id].get("guard_paths", []):
                    self.assertTrue((ROOT / path).exists())
                for rule in matrix[case_id].get("reference_rules", []):
                    self.assertIsInstance(rule, str)
                    self.assertTrue(rule)


class PurposeFitScoringTests(unittest.TestCase):
    def setUp(self):
        self.case = next(case for case in load_cases("core-policy") if case["id"] == "c01-drf-order-api")

    def test_drf_output_fails_critical_gate(self):
        text = "\n".join(
            [
                "DRF ViewSet으로 구현합니다.",
                "from rest_framework import serializers",
                "class OrderSerializer(serializers.ModelSerializer):",
                "    pass",
            ]
        )

        score = score_outputs.score_text(self.case, "without-dddjango", text)

        self.assertEqual(score["gate_status"], "fail")
        self.assertLessEqual(score["total_score"], 59)
        failed_gates = {result["gate"] for result in score["gate_results"] if result["status"] == "fail"}
        self.assertIn("no_drf", failed_gates)

    def test_django_ninja_output_passes_core_policy_gate(self):
        text = "\n".join(
            [
                "이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다.",
                "실제 테스트는 실행하지 않았습니다. 실행할 명령을 제시합니다.",
                "from ninja import Router, Schema",
                "router = Router()",
                "@router.post('/orders', response={201: OrderOut, 400: ProblemDetail})",
                "class OrderIn(Schema):",
                "    pass",
                "python manage.py check",
                "pytest",
            ]
        )

        score = score_outputs.score_text(self.case, "with-dddjango", text)

        self.assertEqual(score["gate_status"], "pass")
        self.assertGreaterEqual(score["total_score"], 80)
        self.assertEqual(score["score_kind"], "automatic_signal")
        self.assertTrue(score["manual_required"])
        self.assertIn("signal_results", score)
        self.assertIn("structural_checks", score)

    def test_drf_rejection_text_does_not_fail_when_no_drf_code_is_generated(self):
        text = "\n".join(
            [
                "이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다.",
                "APIView와 ModelSerializer는 금지 대상이므로 코드에 사용하지 않습니다.",
                "실제 테스트는 실행하지 않았습니다. 실행할 명령을 제시합니다.",
                "from ninja import Router, Schema",
                "router = Router()",
                "class OrderIn(Schema):",
                "    pass",
                "@router.post('/orders', response={201: OrderOut, 400: ProblemDetail})",
                "def create_order(request, payload: OrderIn):",
                "    pass",
            ]
        )

        score = score_outputs.score_text(self.case, "with-dddjango", text)
        failed_gates = {result["gate"] for result in score["gate_results"] if result["status"] == "fail"}

        self.assertNotIn("no_drf", failed_gates)

    def test_false_execution_claim_fails_even_with_command_hint(self):
        text = "\n".join(
            [
                "이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다.",
                "from ninja import Router, Schema",
                "router = Router()",
                "class OrderIn(Schema):",
                "    pass",
                "@router.post('/orders', response={201: OrderOut, 400: ProblemDetail})",
                "테스트가 통과했습니다.",
                "실행할 명령: pytest",
            ]
        )

        score = score_outputs.score_text(self.case, "with-dddjango", text)
        failed_gates = {result["gate"] for result in score["gate_results"] if result["status"] == "fail"}

        self.assertIn("no_false_execution", failed_gates)

    def test_korean_first_requires_more_than_one_hangul_token(self):
        text = "\n".join(
            [
                "한국어",
                "Use Django Ninja Router and Schema for this endpoint.",
                "Return a Problem Details response for validation errors.",
                "Explain the implementation steps and test commands.",
                "from ninja import Router, Schema",
                "router = Router()",
                "class OrderIn(Schema):",
                "    pass",
                "@router.post('/orders', response={201: OrderOut, 400: ProblemDetail})",
            ]
        )

        score = score_outputs.score_text(self.case, "with-dddjango", text)
        failed_gates = {result["gate"] for result in score["gate_results"] if result["status"] == "fail"}

        self.assertIn("korean_first", failed_gates)

    def test_korean_first_ignores_fenced_code_blocks(self):
        text = "\n".join(
            [
                "이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다.",
                "아래 코드는 주문 생성 API의 예시이며, 테스트는 실행하지 않았습니다.",
                "```python",
                "from ninja import Router, Schema",
                "router = Router()",
                "class OrderIn(Schema):",
                "    pass",
                "@router.post('/orders', response={201: OrderOut, 400: ProblemDetail})",
                "def create_order(request, payload: OrderIn):",
                "    return 201, {}",
                "```",
            ]
        )

        score = score_outputs.score_text(self.case, "with-dddjango", text)
        failed_gates = {result["gate"] for result in score["gate_results"] if result["status"] == "fail"}

        self.assertNotIn("korean_first", failed_gates)

    def test_keyword_stuffing_does_not_get_full_score(self):
        case = next(case for case in load_cases("holdout-adversarial") if case["id"] == "h02-keyword-bait-order-design")
        text = "\n".join(
            [
                "Router Schema response={ 애그리거트 transaction idempotency pytest RED GREEN REFACTOR",
                "불변식 유스케이스 근거 검증",
            ]
        )

        score = score_outputs.score_text(case, "with-dddjango", text)

        self.assertEqual(score["gate_status"], "fail")
        self.assertLessEqual(score["total_score"], 59)

    def test_legacy_drf_context_is_allowed_when_marked_as_before_code(self):
        case = next(case for case in load_cases("holdout-adversarial") if case["id"] == "h01-drf-before-after-migration")
        text = "\n".join(
            [
                "기존 legacy 코드는 분석 대상으로만 봅니다.",
                "```python",
                "from rest_framework import serializers, viewsets",
                "class LegacyOrderViewSet(viewsets.ModelViewSet):",
                "    pass",
                "```",
                "새 코드는 Django Ninja로 작성합니다.",
                "from ninja import Router, Schema",
                "router = Router()",
                "class OrderIn(Schema):",
                "    pass",
                "@router.post('/orders', response={201: OrderOut, 400: ProblemDetail})",
                "마이그레이션 단계와 테스트 검증 명령을 제시합니다.",
                "실제 테스트는 실행하지 않았습니다.",
            ]
        )

        score = score_outputs.score_text(case, "with-dddjango", text)
        failed_gates = {result["gate"] for result in score["gate_results"] if result["status"] == "fail"}

        self.assertNotIn("no_drf", failed_gates)

    def test_project_structure_requires_domain_api_service_and_tests(self):
        case = next(case for case in load_cases("code-structure") if case["id"] == "p01-order-feature-file-tree")
        text = "\n".join(
            [
                "domain/ 에 애그리거트와 불변식을 둡니다.",
                "orders/services.py 에 유스케이스와 책임 분리를 둡니다.",
                "파일별 책임과 검증 명령을 함께 제시합니다.",
                "api/schemas.py 와 api/routers.py 에 Router, Schema, response={201: OrderOut, 400: ProblemDetail}를 둡니다.",
                "from ninja import Router, Schema",
                "router = Router()",
                "class OrderIn(Schema): pass",
                "@router.post('/orders', response={201: OrderOut, 400: ProblemDetail})",
                "tests/test_create_order.py 에 pytest RED GREEN REFACTOR 테스트를 둡니다.",
                "Result와 도메인 예외로 실패를 표현합니다.",
                "실제 테스트는 실행하지 않았습니다.",
            ]
        )

        score = score_outputs.score_text(case, "with-dddjango", text)

        self.assertEqual(score["gate_status"], "pass")
        self.assertEqual(score["structural_checks"]["project_structure"]["status"], "pass")
        self.assertGreaterEqual(score["dimension_scores"]["project_structure"], 80)

    def test_reference_usage_requires_reference_rules_not_only_keywords(self):
        case = next(case for case in load_cases("code-structure") if case["id"] == "p02-domain-code-quality")
        text = "\n".join(
            [
                "Result 도메인 예외 값 객체 pytest RED GREEN REFACTOR",
                "타입 책임 경계 실패 중복",
                "실제 테스트는 실행하지 않았습니다.",
            ]
        )

        score = score_outputs.score_text(case, "with-dddjango", text)

        self.assertEqual(score["structural_checks"]["reference_usage"]["status"], "pass")

    def test_simple_task_subagent_ceremony_fails(self):
        case = next(case for case in load_cases("subagent-workflow") if case["id"] == "s02-simple-no-delegation")
        text = "\n".join(
            [
                "## Role Map",
                "- Coordinator",
                "- Domain Agent",
                "필드명 변경은 이렇게 진행합니다.",
            ]
        )

        score = score_outputs.score_text(case, "with-dddjango", text)
        failed_gates = {result["gate"] for result in score["gate_results"] if result["status"] == "fail"}

        self.assertIn("subagent_no_ceremony_for_simple_task", failed_gates)
        self.assertLessEqual(score["total_score"], 59)

    def test_false_subagent_claim_extended_patterns_fail(self):
        case = next(case for case in load_cases("subagent-workflow") if case["id"] == "s05-false-subagent-claim")
        text = "\n".join(
            [
                "Domain Agent에게 맡겼고 결과를 받았습니다.",
                "DB Agent와 API Agent가 병렬 검토했습니다.",
                "계획을 통합했습니다.",
            ]
        )

        score = score_outputs.score_text(case, "with-dddjango", text)
        failed_gates = {result["gate"] for result in score["gate_results"] if result["status"] == "fail"}

        self.assertIn("no_false_subagents", failed_gates)
        self.assertLessEqual(score["total_score"], 59)

    def test_subagent_structural_checks_require_role_table_and_handoff(self):
        case = next(case for case in load_cases("subagent-workflow") if case["id"] == "s03-parallel-safe-review")
        text = "\n".join(
            [
                "## Role Map",
                "| Role | Responsibility | dddjango skills | File ownership |",
                "| Coordinator | 통합 | workflow-dddjango-subagents | final |",
                "| Domain Agent | 도메인 계약 | architecture-ddd | domain/** |",
                "| DB Agent | transaction 검토 | architecture-db | read-only |",
                "| API Agent | Router Schema response={ API contract | architecture-api, implementation-django-ninja | read-only |",
                "| Test Agent | RED pytest | implementation-tdd, implementation-test | read-only |",
                "| Review Agent | 검토 | implementation-cleancode | read-only |",
                "",
                "도메인 계약을 먼저 세운 뒤 읽기 전용 병렬 검토를 진행합니다.",
                "실제로 실행하지 않았습니다.",
                "",
                "## Handoff Contract",
                "- Scope",
                "- Inputs Used",
                "- Decisions",
                "- Files",
                "- Output",
                "- Risks",
                "- Required Follow-up",
                "- dddjango Checks",
                "",
                "## Integration Checklist",
                "- conflict priority",
                "- 도메인 불변식",
                "- transaction",
                "- API contract",
                "- test",
                "- 파일 수정하지 않음",
                "",
                "검증 명령만 제시합니다.",
            ]
        )

        score = score_outputs.score_text(case, "with-dddjango", text)

        self.assertEqual(score["gate_status"], "pass")
        self.assertEqual(score["structural_checks"]["subagent_handoff_contract"]["status"], "pass")
        self.assertEqual(score["structural_checks"]["subagent_execution_planning"]["status"], "pass")
        self.assertGreaterEqual(score["dimension_scores"]["subagent_integration_verification"], 80)


class PurposeFitReportTests(unittest.TestCase):
    def test_fixture_run_scores_and_renders_html_report(self):
        run_dir = run_evaluation.create_run(
            suite="core-policy",
            case_id="c01-drf-order-api",
            variant=None,
            mode="fixture",
        )
        self.addCleanup(lambda: self.cleanup_run(run_dir))

        summary = score_outputs.score_run(run_dir, suite="core-policy")
        report_path = render_report.render_report(run_dir, suite="core-policy")

        self.assertTrue(report_path.exists())
        report = report_path.read_text()
        self.assertIn("baseline", report)
        self.assertIn("without-dddjango", report)
        self.assertIn("with-dddjango", report)
        self.assertIn("Variant Comparison", report)
        self.assertIn("플러그인 성능 평가가 아닙니다", report)
        self.assertIn("Skill value delta: <strong>not applicable</strong>", report)
        self.assertTrue((run_dir / "artifacts/c01-drf-order-api.baseline.html").exists())
        self.assertTrue((run_dir / "artifacts/c01-drf-order-api.with-dddjango.html").exists())
        self.assertIn("by_variant", summary)
        self.assertEqual(summary["release_gate_status"]["status"], "not_applicable")
        self.assertIn("Release Gates", report)

    def test_missing_output_is_scored_as_failure(self):
        run_dir = run_evaluation.create_run(
            suite="core-policy",
            case_id="c01-drf-order-api",
            variant="with-dddjango",
            mode="fixture",
        )
        self.addCleanup(lambda: self.cleanup_run(run_dir))

        summary = score_outputs.score_run(run_dir, suite="core-policy")
        missing = [
            score for score in summary["scores"]
            if score["case_id"] == "c01-drf-order-api"
            and score["variant"] == "without-dddjango"
        ][0]

        self.assertEqual(missing["score_kind"], "missing_output")
        self.assertEqual(missing["total_score"], 0)
        self.assertEqual(missing["gate_status"], "fail")

    def test_live_release_gate_counts_with_dddjango_policy_failures_only(self):
        scores = []
        for case in load_cases():
            scores.append({
                "case_id": case["id"],
                "variant": "without-dddjango",
                "total_score": 80,
                "gate_status": "pass",
                "gate_results": [],
                "dimension_scores": {dimension: 80 for dimension in case["required_dimensions"]},
                "rationale": "pass",
                "automatic_confidence": "high",
                "manual_required": False,
            })
            scores.append({
                "case_id": case["id"],
                "variant": "with-dddjango",
                "total_score": 100,
                "gate_status": "pass",
                "gate_results": [],
                "dimension_scores": {dimension: 100 for dimension in case["required_dimensions"]},
                "rationale": "pass",
                "automatic_confidence": "high",
                "manual_required": False,
            })

        summary = score_outputs.summarize(scores, mode="live")

        self.assertEqual(summary["skill_value_delta"], 20)
        self.assertEqual(summary["release_gate_status"]["status"], "pass")
        gate_ids = {result["gate"] for result in summary["release_gate_status"]["results"]}
        self.assertIn("drf_rejection", gate_ids)
        self.assertIn("api_tdd_core", gate_ids)
        self.assertIn("reference_max", gate_ids)
        self.assertIn("subagent_workflow", gate_ids)
        self.assertIn("code_structure_quality", gate_ids)

    def test_live_release_gate_needs_review_for_low_confidence_automatic_scores(self):
        scores = []
        for case in load_cases():
            scores.append({
                "case_id": case["id"],
                "variant": "without-dddjango",
                "total_score": 80,
                "gate_status": "pass",
                "gate_results": [],
                "dimension_scores": {dimension: 80 for dimension in case["required_dimensions"]},
                "rationale": "pass",
                "automatic_confidence": "high",
                "manual_required": False,
            })
            scores.append({
                "case_id": case["id"],
                "variant": "with-dddjango",
                "total_score": 100,
                "gate_status": "pass",
                "gate_results": [],
                "dimension_scores": {dimension: 100 for dimension in case["required_dimensions"]},
                "rationale": "pass",
                "automatic_confidence": "low",
                "manual_required": True,
            })

        summary = score_outputs.summarize(scores, mode="live")

        self.assertEqual(summary["release_gate_status"]["status"], "needs_review")
        gate_ids = {result["gate"] for result in summary["release_gate_status"]["results"]}
        self.assertIn("manual_review_required", gate_ids)

    def test_partial_live_run_does_not_apply_release_gate(self):
        scores = [
            {
                "case_id": "c01-drf-order-api",
                "variant": "with-dddjango",
                "total_score": 100,
                "gate_status": "pass",
                "gate_results": [],
                "dimension_scores": {"drf_rejection": 100},
                "rationale": "pass",
            }
        ]
        summary = score_outputs.summarize(scores, mode="live")
        metadata = {
            "mode": "live",
            "suite": None,
            "case_id": "c01-drf-order-api",
            "variants": ["with-dddjango"],
            "case_count": 1,
        }

        release = score_outputs.release_gate_status(summary, mode="live", metadata=metadata)

        self.assertEqual(release["status"], "not_applicable")

    def test_latest_run_ignores_calibration_directories(self):
        calibration_dir = ROOT / "workspace/codex-eval/purpose-fit/calibration-99999999"
        run_dir = ROOT / "workspace/codex-eval/purpose-fit/99999999-000000-000000"
        calibration_dir.mkdir(parents=True, exist_ok=True)
        run_dir.mkdir(parents=True, exist_ok=True)
        (calibration_dir / "calibration-report.json").write_text("{}\n")
        (run_dir / "metadata.json").write_text("{}\n")
        self.addCleanup(lambda: self.cleanup_run(calibration_dir))
        self.addCleanup(lambda: self.cleanup_run(run_dir))

        self.assertEqual(latest_run_dir(), run_dir)

    def test_eval_dddjango_target_uses_live_mode(self):
        makefile = (ROOT / "Makefile").read_text()

        self.assertIn("run_evaluation.py --mode live", makefile)
        self.assertNotIn("아직 live dddjango 평가는 준비되지 않았습니다", makefile)

    def test_live_without_dddjango_command_ignores_user_config_and_rules(self):
        command = run_evaluation.codex_command(
            variant="without-dddjango",
            output_path=Path("out.md"),
            work_dir=Path("work"),
        )

        self.assertIn("--ignore-user-config", command)
        self.assertIn("--ignore-rules", command)
        self.assertEqual(command[-1], "-")

    def test_live_failed_codex_execution_writes_auditable_output(self):
        case = next(case for case in load_cases("core-policy") if case["id"] == "c01-drf-order-api")
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir)
            (run_dir / "outputs").mkdir()
            (run_dir / "artifacts").mkdir()
            completed = subprocess.CompletedProcess(
                args=["codex"],
                returncode=127,
                stdout="",
                stderr="codex not found",
            )
            with mock.patch.object(run_evaluation.subprocess, "run", return_value=completed):
                metadata = run_evaluation.run_live_case(case, "with-dddjango", run_dir)

            output_path = run_dir / metadata["output"]
            stderr_path = run_dir / metadata["stderr"]
            self.assertEqual(metadata["exit_status"], 127)
            self.assertTrue(output_path.exists())
            self.assertTrue(stderr_path.exists())
            self.assertIn("Codex live execution failed", output_path.read_text())

    def test_calibration_samples_match_expected_outcomes(self):
        report = run_calibration.run_calibration()

        self.assertEqual(report["status"], "pass")
        self.assertGreaterEqual(report["sample_count"], 11)

    def cleanup_run(self, run_dir):
        for path in sorted(run_dir.rglob("*"), reverse=True):
            path.unlink() if path.is_file() else path.rmdir()
        run_dir.rmdir()


if __name__ == "__main__":
    unittest.main()
