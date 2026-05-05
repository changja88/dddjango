import importlib.util
import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "evals/codex/cases/pilot.jsonl"
BENCHMARK_CASES_PATH = ROOT / "evals/shared/cases/benchmark.jsonl"
HARD_BENCHMARK_CASES_PATH = ROOT / "evals/shared/cases/hard-benchmark.jsonl"
TARGETED_RERUN_CASES_PATH = ROOT / "evals/shared/cases/targeted-rerun.jsonl"
CONFORMANCE_RERUN_CASES_PATH = ROOT / "evals/shared/cases/conformance-rerun.jsonl"
TRIGGER_CASES_PATH = ROOT / "evals/shared/cases/trigger.jsonl"
REAL_REPO_CASES_PATH = ROOT / "evals/shared/cases/real-repo.jsonl"
REFERENCE_MAP_PATH = ROOT / "evals/codex/reference-map.json"
CONFORMANCE_MAP_PATH = ROOT / "evals/codex/conformance-map.json"
REAL_REPO_FIXTURE_PATH = ROOT / "evals/fixtures/django-shop"
SCHEMA_PATH = ROOT / "evals/codex/rubrics/grading-schema.json"
CONFORMANCE_SCHEMA_PATH = ROOT / "evals/codex/rubrics/dddjango-conformance-schema.json"
USABILITY_CHECKLIST_PATH = ROOT / "evals/shared/rubrics/usability-checklist.md"
GRADE_SCRIPT_PATH = ROOT / "evals/codex/scripts/grade_outputs.py"
AUTO_GRADE_SCRIPT_PATH = ROOT / "evals/codex/scripts/auto_grade_outputs.py"
CONFORMANCE_SCRIPT_PATH = ROOT / "evals/codex/scripts/grade_conformance.py"
INIT_SCRIPT_PATH = ROOT / "evals/codex/scripts/init_iteration.py"
RUN_SCRIPT_PATH = ROOT / "evals/codex/scripts/run_prompts.py"
REPORT_SCRIPT_PATH = ROOT / "evals/codex/scripts/render_report.py"
REPEAT_REPORT_SCRIPT_PATH = ROOT / "evals/codex/scripts/render_repeat_summary.py"
REAL_REPO_DIFF_SCRIPT_PATH = ROOT / "evals/codex/scripts/evaluate_real_repo_diffs.py"
POLICY_SKILL_PATHS = [
    "implementation-django-ninja",
    "architecture-api",
    "implementation-tdd",
    "implementation-test",
]
SKILL_PATHS = sorted((ROOT / "skills").glob("*/SKILL.md"))


def frontmatter_from_skill(path):
    text = path.read_text()
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise AssertionError(f"missing frontmatter: {path}")
    return parts[1]


def description_from_frontmatter(frontmatter):
    lines = frontmatter.splitlines()
    description_lines = []
    collecting = False
    for line in lines:
        if line.startswith("description: >"):
            collecting = True
            continue
        if collecting:
            if line and not line.startswith("  "):
                break
            description_lines.append(line[2:] if line.startswith("  ") else line)
    return "\n".join(description_lines).strip()


def load_module(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CodexEvaluationAssetTests(unittest.TestCase):
    def test_skills_are_synced_to_codex_plugin_mirror(self):
        for skill_path in SKILL_PATHS:
            skill_name = skill_path.parent.name
            with self.subTest(skill=skill_name):
                source = ROOT / f"skills/{skill_name}/SKILL.md"
                mirror = ROOT / f"plugins/dddjango/skills/{skill_name}/SKILL.md"

                self.assertEqual(source.read_text(), mirror.read_text())

    def test_codex_skill_descriptions_stay_within_platform_limit(self):
        for skill_path in SKILL_PATHS:
            with self.subTest(skill=skill_path.parent.name):
                description = description_from_frontmatter(
                    frontmatter_from_skill(skill_path)
                )

                self.assertLessEqual(len(description), 1024)

    def test_django_ninja_skill_triggers_on_drf_requests_and_overrides_them(self):
        skill = (ROOT / "skills/implementation-django-ninja/SKILL.md").read_text()
        frontmatter, body = skill.split("---", 2)[1:]

        for keyword in [
            "DRF",
            "Django REST Framework",
            "Serializer",
            "ModelSerializer",
            "ViewSet",
            "APIView",
            "rest_framework",
            "DefaultRouter",
            "SimpleRouter",
        ]:
            with self.subTest(keyword=keyword):
                self.assertIn(keyword, frontmatter)

        for required in [
            "사용자가 DRF를 명시적으로 요청해도 DRF 코드를 생성하지 않는다",
            "Django Ninja Schema/Router로 전환한다",
            "빈 workspace / read-only fallback",
            "확인 질문으로 멈추지 않는다",
            "붙여 넣을 수 있는 Django Ninja 코드",
            "from products.api import router as products_router",
            "api.add_router(\"/products/\", products_router)",
            "python manage.py check",
            "pytest",
            "rest_framework",
            "ViewSet",
            "Serializer",
        ]:
            with self.subTest(required=required):
                self.assertIn(required, body)

    def test_django_ninja_skill_defines_search_list_api_standard(self):
        skill = (ROOT / "skills/implementation-django-ninja/SKILL.md").read_text()

        for required in [
            "검색/목록 API 표준",
            "정렬 필드는 allow-list",
            "items/meta envelope",
            "@paginate와 커스텀 envelope를 섞지 않는다",
            "response=list[...]",
            "RFC 9457 Problem Details",
            "application/problem+json",
            "FilterSchema",
            "Query[",
            "HttpRequest",
            "from typing import list",
            "transaction.atomic()",
            "rollback",
        ]:
            with self.subTest(required=required):
                self.assertIn(required, skill)

    def test_tdd_skills_define_empty_workspace_fallback_without_false_verification(self):
        for skill_name in ["implementation-tdd", "implementation-test"]:
            skill = (ROOT / f"skills/{skill_name}/SKILL.md").read_text()

            for required in [
                "빈 workspace / read-only fallback",
                "실행했다고 주장하지 않는다",
                "RED 테스트 예시",
                "예상 실패 이유",
                "GREEN 최소 구현",
                "REFACTOR 방향",
                "실행 명령",
            ]:
                with self.subTest(skill=skill_name, required=required):
                    self.assertIn(required, skill)

    def test_tdd_skill_triggers_on_django_pytest_red_green_refactor_requests(self):
        frontmatter = frontmatter_from_skill(
            ROOT / "skills/implementation-tdd/SKILL.md"
        )

        for keyword in [
            "Django",
            "pytest",
            "쿠폰",
            "실패 테스트",
            "Red-Green-Refactor",
            "empty workspace",
            "read-only",
        ]:
            with self.subTest(keyword=keyword):
                self.assertIn(keyword, frontmatter)

    def test_low_lift_skill_updates_define_hard_case_outputs(self):
        tdd = (ROOT / "skills/implementation-tdd/SKILL.md").read_text()
        cleancode = (ROOT / "skills/implementation-cleancode/SKILL.md").read_text()

        for required in [
            "도메인 정책 TDD 산출물",
            "정상",
            "경계",
            "실패",
            "멱등성/중복 요청",
            "명시적 결과 타입",
            "CancelOrderResult",
            "TransitionOrderStatusResult",
            "ReserveInventoryResult",
            "transaction 적용 지점",
        ]:
            with self.subTest(skill="implementation-tdd", required=required):
                self.assertIn(required, tdd)

        for required in [
            "원칙 설명만 나열하지 않는다",
            "Before/After",
            "unified diff",
            "dict/None/error-code 반환",
            "Protocol 기반 port",
        ]:
            with self.subTest(skill="implementation-cleancode", required=required):
                self.assertIn(required, cleancode)

    def test_pilot_cases_define_representative_codex_plugin_eval_set(self):
        cases = [
            json.loads(line)
            for line in CASES_PATH.read_text().splitlines()
            if line.strip()
        ]

        self.assertEqual(len(cases), 8)
        self.assertEqual(len({case["id"] for case in cases}), 8)

        categories = {case["category"] for case in cases}
        self.assertEqual(
            categories,
            {
                "api-design",
                "db-design",
                "implementation",
                "negative-control",
                "review",
                "tdd",
            },
        )

        for case in cases:
            self.assertTrue(case["prompt"].strip())
            self.assertTrue(case["title"].strip())
            self.assertIn("korean_first", case["expectations"])
            self.assertIn("django_ninja_compliance", case["expectations"])
            self.assertTrue(case["scoring_focus"])

        drf_case = next(case for case in cases if case["id"] == "pilot-negative-drf")
        self.assertIn("reject_drf", drf_case["expectations"])
        self.assertIn("Django Ninja", " ".join(drf_case["scoring_focus"]))

    def test_benchmark_cases_define_full_skill_eval_set(self):
        cases = [
            json.loads(line)
            for line in BENCHMARK_CASES_PATH.read_text().splitlines()
            if line.strip()
        ]

        self.assertEqual(len(cases), 24)
        self.assertEqual(len({case["id"] for case in cases}), 24)

        category_counts = {}
        for case in cases:
            category_counts[case["category"]] = category_counts.get(case["category"], 0) + 1
            self.assertTrue(case["prompt"].strip())
            self.assertTrue(case["title"].strip())
            self.assertIn("korean_first", case["expectations"])
            self.assertTrue(case["scoring_focus"])

        self.assertEqual(
            category_counts,
            {
                "api-design": 4,
                "ddd-architecture": 4,
                "db-design": 3,
                "tdd": 4,
                "review": 4,
                "clean-code": 3,
                "negative-control": 2,
            },
        )

        drf_cases = [case for case in cases if "reject_drf" in case["expectations"]]
        self.assertTrue(drf_cases)
        for case in drf_cases:
            self.assertIn("DRF", case["prompt"])
            self.assertIn("Django Ninja", " ".join(case["scoring_focus"]))

    def test_hard_benchmark_cases_target_known_low_lift_areas(self):
        cases = [
            json.loads(line)
            for line in HARD_BENCHMARK_CASES_PATH.read_text().splitlines()
            if line.strip()
        ]

        self.assertEqual(len(cases), 8)
        self.assertEqual(len({case["id"] for case in cases}), 8)
        self.assertEqual(
            {case["category"] for case in cases},
            {"api-design", "db-design", "tdd", "clean-code", "negative-control"},
        )

        case_text = json.dumps(cases, ensure_ascii=False)
        for required in [
            "hard-negative-fastapi-korean",
            "hard-tdd-domain-policy-red-green",
            "hard-clean-fat-model-policy-extraction",
            "hard-api-drf-migration-no-imports",
            "Django Ninja",
            "RED/GREEN/REFACTOR",
            "FastAPI",
        ]:
            with self.subTest(required=required):
                self.assertIn(required, case_text)

    def test_targeted_rerun_cases_pin_known_low_lift_regressions(self):
        cases = [
            json.loads(line)
            for line in TARGETED_RERUN_CASES_PATH.read_text().splitlines()
            if line.strip()
        ]

        self.assertEqual(
            {case["id"] for case in cases},
            {
                "benchmark-negative-fastapi",
                "benchmark-tdd-domain-policy",
                "benchmark-tdd-inventory-reserve",
                "benchmark-clean-refactor-model-method",
            },
        )
        self.assertEqual(len(cases), 4)

    def test_conformance_rerun_cases_target_remaining_rule_pass_gaps(self):
        cases = [
            json.loads(line)
            for line in CONFORMANCE_RERUN_CASES_PATH.read_text().splitlines()
            if line.strip()
        ]

        self.assertEqual(
            {case["id"] for case in cases},
            {
                "benchmark-db-order-query-index",
                "benchmark-db-payment-ledger",
                "benchmark-db-refund-transaction",
                "benchmark-tdd-ninja-endpoint",
                "benchmark-tdd-order-cancel",
            },
        )
        self.assertEqual(len(cases), 5)
        case_text = json.dumps(cases, ensure_ascii=False)
        for required in [
            "migration 검증",
            "조회 패턴",
            "Result Type",
            "도메인 예외",
            "edge case",
        ]:
            with self.subTest(required=required):
                self.assertIn(required, case_text)

    def test_trigger_cases_define_precision_recall_eval_set(self):
        cases = [
            json.loads(line)
            for line in TRIGGER_CASES_PATH.read_text().splitlines()
            if line.strip()
        ]

        self.assertEqual(len(cases), 30)
        self.assertEqual(len({case["id"] for case in cases}), 30)

        trigger_counts = {}
        for case in cases:
            trigger_type = case["trigger_type"]
            trigger_counts[trigger_type] = trigger_counts.get(trigger_type, 0) + 1
            self.assertEqual(case["category"], "trigger")
            self.assertTrue(case["prompt"].strip())
            self.assertTrue(case["expected_behavior"].strip())
            self.assertIn("korean_first", case["expectations"])
            self.assertTrue(case["scoring_focus"])

        self.assertEqual(
            trigger_counts,
            {
                "positive": 10,
                "negative": 10,
                "ambiguous": 6,
                "conflict": 4,
            },
        )

    def test_real_repo_fixture_has_representative_django_project(self):
        expected_files = [
            "README.md",
            "manage.py",
            "config/settings.py",
            "config/urls.py",
            "shop/orders/models.py",
            "shop/orders/views.py",
            "shop/orders/api_drf.py",
            "shop/orders/tests.py",
        ]

        for relative_path in expected_files:
            with self.subTest(path=relative_path):
                self.assertTrue((REAL_REPO_FIXTURE_PATH / relative_path).exists())

        models = (REAL_REPO_FIXTURE_PATH / "shop/orders/models.py").read_text()
        views = (REAL_REPO_FIXTURE_PATH / "shop/orders/views.py").read_text()
        legacy_drf = (REAL_REPO_FIXTURE_PATH / "shop/orders/api_drf.py").read_text()

        self.assertIn("class Order", models)
        self.assertIn("def cancel", models)
        self.assertIn("transaction.atomic", views)
        self.assertIn("JsonResponse", views)
        self.assertIn("rest_framework", legacy_drf)
        self.assertIn("ModelSerializer", legacy_drf)

    def test_real_repo_cases_define_forward_eval_set(self):
        cases = [
            json.loads(line)
            for line in REAL_REPO_CASES_PATH.read_text().splitlines()
            if line.strip()
        ]

        self.assertEqual(len(cases), 6)
        self.assertEqual(len({case["id"] for case in cases}), 6)
        self.assertEqual(
            {case["id"] for case in cases},
            {
                "real-repo-fat-model-refactor",
                "real-repo-ninja-product-search",
                "real-repo-pytest-coupon",
                "real-repo-db-order-index-review",
                "real-repo-view-logic-service-layer",
                "real-repo-drf-to-ninja-migration",
            },
        )

        for case in cases:
            with self.subTest(case=case["id"]):
                self.assertEqual(case["fixture"], "evals/fixtures/django-shop")
                self.assertEqual(case["mode"], "forward-diff")
                self.assertIn("korean_first", case["expectations"])
                self.assertIn("real_repo_applicability", case["expectations"])
                self.assertIn("unified diff", case["prompt"])
                self.assertTrue(case["scoring_focus"])

    def test_reference_map_defines_ceiling_eval_inputs_without_answer_leakage(self):
        reference_map = json.loads(REFERENCE_MAP_PATH.read_text())

        self.assertEqual(reference_map["version"], 1)
        self.assertIn("case_defaults", reference_map)
        self.assertIn("cases", reference_map)
        self.assertIn("api-design", reference_map["case_defaults"])

        for case_id in [
            "pilot-negative-drf",
            "pilot-tdd-coupon",
            "benchmark-api-product-search",
            "benchmark-db-order-query-index",
        ]:
            with self.subTest(case=case_id):
                self.assertIn(case_id, reference_map["cases"])
                mapping = reference_map["cases"][case_id]
                self.assertTrue(mapping["references"])
                self.assertTrue(mapping["expected_rules"])
                self.assertNotIn("answer", json.dumps(mapping).lower())
                for relative_path in mapping["references"]:
                    self.assertTrue((ROOT / relative_path).exists(), relative_path)

    def test_grading_schema_weights_sum_to_100(self):
        schema = json.loads(SCHEMA_PATH.read_text())

        criteria = schema["criteria"]
        self.assertEqual(sum(item["weight"] for item in criteria), 100)
        self.assertEqual(
            [item["id"] for item in criteria],
            [
                "domain_fit",
                "django_ninja_compliance",
                "actionability",
                "architecture_quality",
                "testing_quality",
                "korean_first",
                "conciseness",
                "safety",
            ],
        )

        thresholds = schema["success_thresholds"]
        self.assertEqual(thresholds["minimum_average_lift_points"], 3)
        self.assertEqual(thresholds["minimum_ceiling_normalized_lift_percent"], 25)
        self.assertEqual(thresholds["quality_lift_score_ceiling"], 95)
        self.assertEqual(thresholds["maximum_drf_violation_count"], 0)

    def test_conformance_schema_and_map_define_dddjango_specific_release_gate(self):
        schema = json.loads(CONFORMANCE_SCHEMA_PATH.read_text())
        conformance_map = json.loads(CONFORMANCE_MAP_PATH.read_text())

        self.assertEqual(schema["version"], 1)
        self.assertEqual(conformance_map["version"], 1)
        self.assertEqual(
            schema["release_gate"],
            conformance_map["release_gate"],
        )
        self.assertEqual(
            conformance_map["release_gate"]["minimum_dddjango_conformance_score"],
            85,
        )
        self.assertIn("dddjango_variant", schema["summary_fields"])

        for category in [
            "api-design",
            "db-design",
            "tdd",
            "clean-code",
            "negative-control",
        ]:
            with self.subTest(category=category):
                config = conformance_map["category_defaults"][category]
                self.assertTrue(config["required_rules"])

        for category in ["api-design", "tdd", "clean-code", "negative-control"]:
            with self.subTest(critical_category=category):
                self.assertTrue(
                    conformance_map["category_defaults"][category]["critical_rules"]
                )

        api_rules = conformance_map["category_defaults"]["api-design"]["required_rules"]
        self.assertIn("uses_django_ninja_router", api_rules)
        self.assertIn("no_drf_code", api_rules)
        self.assertIn(
            "uses_problem_details",
            conformance_map["expectation_rules"]["api_standard"],
        )

        negative_rules = conformance_map["category_defaults"]["negative-control"]["required_rules"]
        self.assertIn("no_django_contamination", negative_rules)
        self.assertIn("honors_requested_non_django_framework", negative_rules)

    def test_usability_checklist_and_schema_define_manual_review_fields(self):
        checklist = USABILITY_CHECKLIST_PATH.read_text()
        schema = json.loads(SCHEMA_PATH.read_text())

        usability_fields = [item["id"] for item in schema["usability_criteria"]]
        self.assertEqual(
            usability_fields,
            [
                "actionable",
                "concise",
                "realistic_file_layout",
                "korean_quality",
            ],
        )

        for item in schema["usability_criteria"]:
            with self.subTest(item=item["id"]):
                self.assertEqual(item["max"], 5)
                self.assertIn(item["label"], checklist)

        for required in [
            "실행 가능한 Django/Ninja 문법",
            "파일 구조와 import",
            "migration, transaction, test",
            "한국어 요청",
            "정책 설명이 과하게 반복",
            "바로 적용 가능한 수준",
        ]:
            with self.subTest(required=required):
                self.assertIn(required, checklist)

    def test_grade_outputs_summarizes_baseline_and_dddjango_scores(self):
        module = load_module(GRADE_SCRIPT_PATH)
        schema = {
            "criteria": [
                {"id": "domain_fit", "weight": 20},
                {"id": "korean_first", "weight": 10},
            ],
            "usability_criteria": [
                {"id": "actionable", "max": 5},
                {"id": "concise", "max": 5},
            ],
        }
        grades = [
            {
                "case_id": "case-1",
                "variant": "baseline",
                "scores": {"domain_fit": 10, "korean_first": 5},
                "usability": {"actionable": 2, "concise": 3, "notes": "plain"},
            },
            {
                "case_id": "case-1",
                "variant": "dddjango",
                "scores": {"domain_fit": 18, "korean_first": 10},
                "usability": {"actionable": 5, "concise": 4, "notes": "usable"},
            },
        ]

        summary = module.summarize_grades(grades, schema)

        self.assertEqual(summary["variants"]["baseline"]["average_score"], 15.0)
        self.assertEqual(summary["variants"]["dddjango"]["average_score"], 28.0)
        self.assertEqual(summary["variants"]["baseline"]["average_usability"], 5.0)
        self.assertEqual(summary["variants"]["dddjango"]["average_usability"], 9.0)
        self.assertEqual(summary["lift"]["absolute"], 13.0)
        self.assertAlmostEqual(summary["lift"]["percent"], 86.67, places=2)

    def test_grade_outputs_excludes_ungraded_template_entries(self):
        module = load_module(GRADE_SCRIPT_PATH)
        schema = {
            "criteria": [
                {"id": "domain_fit", "weight": 20},
                {"id": "korean_first", "weight": 10},
            ]
        }
        grades = [
            {
                "case_id": "case-1",
                "variant": "baseline",
                "scores": {"domain_fit": 10, "korean_first": 5},
                "notes": "graded",
            },
            {
                "case_id": "case-1",
                "variant": "dddjango",
                "scores": {"domain_fit": 0, "korean_first": 0},
                "notes": "",
                "flags": {"korean_first": False},
            },
        ]

        summary = module.summarize_grades(grades, schema)

        self.assertEqual(summary["variants"]["baseline"]["average_score"], 15.0)
        self.assertNotIn("dddjango", summary["variants"])
        self.assertEqual(summary["pending"]["dddjango"], ["case-1"])
        self.assertEqual(summary["lift"], {})

    def test_auto_grade_outputs_scores_markdown_outputs_and_trigger_flags(self):
        module = load_module(AUTO_GRADE_SCRIPT_PATH)

        with tempfile.TemporaryDirectory() as temp_dir:
            iteration = Path(temp_dir)
            (iteration / "baseline").mkdir()
            (iteration / "dddjango").mkdir()
            (iteration / "answer-key").mkdir()
            case = {
                "case_id": "trigger-positive",
                "title": "Positive trigger",
                "category": "trigger",
                "expectations": ["korean_first", "django_ninja_compliance"],
                "trigger_type": "positive",
                "expected_behavior": "Apply dddjango Django Ninja guidance.",
            }
            (iteration / "answer-key/trigger-positive.json").write_text(
                json.dumps(case, ensure_ascii=False) + "\n"
            )
            (iteration / "baseline/trigger-positive.output.md").write_text(
                "Django API를 만들 때 Router와 Schema를 사용할 수 있습니다.\n"
            )
            (iteration / "dddjango/trigger-positive.output.md").write_text(
                "Django Ninja Router와 Schema를 사용하고, 도메인 경계와 "
                "application service를 분리합니다. pytest 검증도 추가합니다. "
                "라우터는 요청과 응답 변환만 담당하고, 상태 변경 규칙은 "
                "도메인 서비스와 애플리케이션 계층에 둡니다.\n"
            )
            scores = {
                "domain_fit": 0,
                "django_ninja_compliance": 0,
                "actionability": 0,
                "architecture_quality": 0,
                "testing_quality": 0,
                "korean_first": 0,
                "conciseness": 0,
                "safety": 0,
            }
            empty_trigger = {
                "type": "positive",
                "expected": "Apply dddjango Django Ninja guidance.",
                "observed": "",
                "passed": False,
            }
            (iteration / "grades.json").write_text(
                json.dumps(
                    [
                        {
                            "case_id": "trigger-positive",
                            "variant": "baseline",
                            "scores": scores,
                            "flags": {},
                            "trigger": empty_trigger,
                        },
                        {
                            "case_id": "trigger-positive",
                            "variant": "dddjango",
                            "scores": scores,
                            "flags": {},
                            "trigger": empty_trigger,
                        },
                    ],
                    ensure_ascii=False,
                )
                + "\n"
            )

            module.auto_grade(iteration)
            grades = json.loads((iteration / "grades.json").read_text())
            dddjango = next(grade for grade in grades if grade["variant"] == "dddjango")

            self.assertGreater(dddjango["scores"]["domain_fit"], 0)
            self.assertTrue(dddjango["flags"]["korean_first"])
            self.assertTrue(dddjango["flags"]["django_ninja_used"])
            self.assertFalse(dddjango["flags"]["drf_endorsed"])
            self.assertTrue(dddjango["trigger"]["passed"])
            self.assertIn("auto heuristic", dddjango["notes"])

    def test_auto_grade_does_not_treat_generic_serializer_word_as_drf(self):
        module = load_module(AUTO_GRADE_SCRIPT_PATH)

        self.assertFalse(
            module.drf_is_endorsed(
                "Django view는 serializer/form 검증 후 application service를 호출합니다."
            )
        )
        self.assertFalse(
            module.drf_is_endorsed(
                "DRF `Serializer`, `ViewSet`, `APIView`는 쓰지 않고 Django Ninja 패턴으로 작성합니다."
            )
        )
        self.assertTrue(
            module.drf_is_endorsed(
                "class ProductSerializer(serializers.ModelSerializer):\n    pass\n"
            )
        )

    def test_auto_grade_recognizes_conditional_ambiguous_handling(self):
        module = load_module(AUTO_GRADE_SCRIPT_PATH)
        case = {
            "trigger_type": "ambiguous",
            "expected_behavior": "Clarify project context.",
        }
        text = (
            "현재 프로젝트 맥락이 불명확합니다. Django 기준으로는 app 내부 "
            "services.py가 기본값이고, 비 Django라면 애플리케이션 계층에 둡니다."
        )

        self.assertTrue(
            module.trigger_passed(
                case,
                text,
                {
                    "korean_first": True,
                    "django_ninja_used": False,
                    "drf_endorsed": False,
                    "negative_control_passed": False,
                },
            )
        )

    def test_auto_grade_scores_api_and_db_architecture_terms(self):
        module = load_module(AUTO_GRADE_SCRIPT_PATH)

        api_case = {
            "id": "benchmark-api-product-search",
            "category": "api-design",
            "expectations": ["django_ninja_compliance", "api_standard"],
        }
        api_text = (
            "Django Ninja Router와 Schema를 사용합니다. 검색 필터, 정렬 allow-list, "
            "페이지네이션 meta, RFC 9457 Problem Details 에러 표준을 둡니다."
        )
        api_scores, _ = module.base_scores(api_case, api_text, "dddjango")
        self.assertGreaterEqual(api_scores["architecture_quality"], 12)

        db_case = {
            "id": "benchmark-db-order-query-index",
            "category": "db-design",
            "expectations": ["db_design"],
        }
        db_text = (
            "대표 쿼리 워크로드를 정하고 EXPLAIN ANALYZE로 Seq Scan, Sort, "
            "actual time을 본 뒤 composite index와 select_related를 검토합니다."
        )
        db_scores, _ = module.base_scores(db_case, db_text, "dddjango")
        self.assertGreaterEqual(db_scores["architecture_quality"], 12)

    def test_auto_grade_uses_boundaries_for_tdd_markers(self):
        module = load_module(AUTO_GRADE_SCRIPT_PATH)

        self.assertFalse(
            module.has_pytest_or_tdd(
                "created_at과 related_name을 정리하고 redirection URL을 바꿉니다."
            )
        )
        for text in [
            "pytest로 회귀 테스트를 작성합니다.",
            "RED-GREEN-REFACTOR 순서로 진행합니다.",
            "실패 테스트를 먼저 추가합니다.",
            "도메인 서비스 테스트를 작성합니다.",
            "test_order_confirm를 추가합니다.",
            "python manage.py check를 실행합니다.",
            "python manage.py makemigrations --check --dry-run을 실행합니다.",
            "python manage.py migrate --plan으로 검증합니다.",
            "EXPLAIN ANALYZE로 대표 쿼리를 확인합니다.",
            "python manage.py test orders를 실행합니다.",
            "assert result.status_code == 201",
        ]:
            with self.subTest(text=text):
                self.assertTrue(module.has_pytest_or_tdd(text))

    def test_auto_grade_negative_control_does_not_reward_django_or_api_terms(self):
        module = load_module(AUTO_GRADE_SCRIPT_PATH)
        case = {
            "id": "benchmark-negative-fastapi",
            "category": "negative-control",
            "expectations": ["negative_control_passed"],
        }
        text = (
            "FastAPI로 구현합니다.\n"
            "pyproject.toml의 name은 dddjango-codex-eval입니다.\n"
            "```python\n"
            "from fastapi import FastAPI\n"
            "app = FastAPI()\n"
            "@app.get('/health')\n"
            "def health():\n"
            "    return {'ok': True}\n"
            "```\n"
        )

        scores, flags = module.base_scores(case, text, "dddjango")

        self.assertTrue(flags["negative_control_passed"])
        self.assertLessEqual(scores["domain_fit"], 11)
        self.assertEqual(scores["architecture_quality"], 7)

    def test_auto_grade_allows_concise_korean_negative_control_answers(self):
        module = load_module(AUTO_GRADE_SCRIPT_PATH)
        case = {
            "id": "hard-negative-fastapi-korean",
            "category": "negative-control",
            "expectations": ["negative_control_passed"],
        }
        text = (
            "FastAPI 기준 최소 health check API 예시입니다.\n"
            "실행 명령과 확인 방법만 짧게 정리합니다.\n"
            "```python\nfrom fastapi import FastAPI\napp = FastAPI()\n```\n"
        )

        scores, flags = module.base_scores(case, text, "dddjango")

        self.assertTrue(flags["korean_first"])
        self.assertEqual(scores["korean_first"], 10)

    def test_grade_conformance_scores_dddjango_convention_rules(self):
        module = load_module(CONFORMANCE_SCRIPT_PATH)

        with tempfile.TemporaryDirectory() as temp_dir:
            iteration = Path(temp_dir)
            (iteration / "baseline").mkdir()
            (iteration / "dddjango").mkdir()
            (iteration / "answer-key").mkdir()
            case = {
                "id": "api-case",
                "title": "API case",
                "category": "api-design",
                "expectations": [
                    "korean_first",
                    "django_ninja_compliance",
                    "api_standard",
                ],
            }
            (iteration / "answer-key/api-case.json").write_text(
                json.dumps(case, ensure_ascii=False) + "\n"
            )
            (iteration / "baseline/api-case.output.md").write_text(
                "DRF ViewSet과 ModelSerializer로 구현합니다.\n"
            )
            (iteration / "dddjango/api-case.output.md").write_text(
                "Django Ninja Router와 Schema를 사용합니다.\n"
                "```python\n"
                "from django.http import HttpRequest\n"
                "from ninja import Router, Schema\n"
                "router = Router()\n"
                "class ProductOut(Schema):\n"
                "    id: int\n"
                "@router.get('/products', response=dict)\n"
                "def list_products(request: HttpRequest) -> dict:\n"
                "    return {'items': [], 'meta': {'total': 0}}\n"
                "```\n"
                "오류는 RFC 9457 Problem Details와 application/problem+json으로 통일합니다.\n"
                "python manage.py check와 pytest로 검증합니다.\n"
            )

            output_path = module.grade_conformance(iteration, map_path=CONFORMANCE_MAP_PATH)
            result = json.loads(output_path.read_text())
            dddjango = next(
                record
                for record in result["cases"]
                if record["variant"] == "dddjango"
            )
            baseline = next(
                record
                for record in result["cases"]
                if record["variant"] == "baseline"
            )

            self.assertGreater(dddjango["conformance_score"], baseline["conformance_score"])
            self.assertIn("uses_django_ninja_router", dddjango["passed_rules"])
            self.assertIn("uses_problem_details", dddjango["passed_rules"])
            self.assertFalse(dddjango["critical_violations"])
            self.assertGreater(result["summary"]["delta"], 0)

    def test_grade_conformance_uses_structural_rule_checks(self):
        module = load_module(CONFORMANCE_SCRIPT_PATH)

        self.assertFalse(module.rule_uses_items_meta_envelope("items와 meta를 설명합니다."))
        self.assertTrue(
            module.rule_uses_items_meta_envelope(
                "return {'items': [], 'meta': {'total': 0}}\n"
            )
        )

        self.assertFalse(module.rule_includes_migration_verification("마이그레이션 검증"))
        self.assertTrue(
            module.rule_includes_migration_verification(
                "python manage.py makemigrations --check\npython manage.py migrate --plan\n"
            )
        )

        self.assertFalse(module.rule_has_result_type("Result Type을 사용합니다."))
        self.assertTrue(
            module.rule_has_result_type(
                "@dataclass(frozen=True)\nclass CancelOrderResult:\n    ok: bool\n"
            )
        )

        late_query_pattern = "\n".join(["일반 설명"] * 45 + ["조회 패턴: status + created_at"])
        early_query_pattern = "조회 패턴: status + created_at\n\nmodels.Index(...)\n"
        self.assertFalse(module.rule_has_query_pattern_first(late_query_pattern))
        self.assertTrue(module.rule_has_query_pattern_first(early_query_pattern))

    def test_grade_conformance_flags_negative_control_contamination(self):
        module = load_module(CONFORMANCE_SCRIPT_PATH)

        self.assertTrue(
            module.rule_no_django_contamination(
                "FastAPI 기준 health check입니다. Django는 사용하지 않습니다."
            )
        )
        self.assertFalse(
            module.rule_no_django_contamination(
                "FastAPI 요청이지만 Django Ninja Router와 DDD 구조를 함께 제안합니다."
            )
        )

    def test_init_iteration_creates_prompt_files_and_grade_template(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "iteration-1"

            subprocess.run(
                [
                    sys.executable,
                    str(INIT_SCRIPT_PATH),
                    "--cases",
                    str(CASES_PATH),
                    "--schema",
                    str(SCHEMA_PATH),
                    "--output",
                    str(output_dir),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            baseline_prompts = sorted((output_dir / "baseline").glob("*.prompt.md"))
            dddjango_prompts = sorted((output_dir / "dddjango").glob("*.prompt.md"))
            answer_keys = sorted((output_dir / "answer-key").glob("*.json"))
            grades = json.loads((output_dir / "grades.json").read_text())
            timing = json.loads((output_dir / "timing.json").read_text())

            self.assertEqual(len(baseline_prompts), 8)
            self.assertEqual(len(dddjango_prompts), 8)
            self.assertEqual(len(answer_keys), 8)
            self.assertEqual(len(grades), 16)
            self.assertEqual(len(timing), 16)
            self.assertTrue((output_dir / "SUMMARY.md").exists())

            first_prompt = baseline_prompts[0].read_text()
            self.assertIn("Variant: baseline", first_prompt)
            self.assertIn("Prompt", first_prompt)
            self.assertNotIn("Fixture path:", first_prompt)
            self.assertNotIn("Expectations", first_prompt)
            self.assertNotIn("Scoring Focus", first_prompt)

            first_answer_key = json.loads(answer_keys[0].read_text())
            self.assertIn("expectations", first_answer_key)
            self.assertIn("scoring_focus", first_answer_key)
            self.assertIn(first_answer_key["prompt"], first_prompt)
            self.assertNotIn(first_answer_key["expectations"][0], first_prompt)
            self.assertNotIn(first_answer_key["scoring_focus"][0], first_prompt)

            first_grade = grades[0]
            self.assertEqual(set(first_grade["scores"]), {
                "domain_fit",
                "django_ninja_compliance",
                "actionability",
                "architecture_quality",
                "testing_quality",
                "korean_first",
                "conciseness",
                "safety",
            })
            self.assertEqual(
                first_grade["usability"],
                {
                    "actionable": 0,
                    "concise": 0,
                    "realistic_file_layout": 0,
                    "korean_quality": 0,
                    "notes": "",
                },
            )
            self.assertIn(first_grade["variant"], {"baseline", "dddjango"})

    def test_init_iteration_clears_stale_generated_outputs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "iteration-1"
            stale_paths = [
                output_dir / "baseline/pilot-api-order-create.output.md",
                output_dir / "baseline/pilot-api-order-create.codex.log",
                output_dir / "dddjango/pilot-api-order-create.output.md",
                output_dir / "report.html",
                output_dir / "conformance.json",
                output_dir / "artifacts/pilot-api-order-create-baseline.html",
            ]
            for path in stale_paths:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("stale\n")

            subprocess.run(
                [
                    sys.executable,
                    str(INIT_SCRIPT_PATH),
                    "--cases",
                    str(CASES_PATH),
                    "--schema",
                    str(SCHEMA_PATH),
                    "--output",
                    str(output_dir),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            for path in stale_paths:
                with self.subTest(path=path):
                    self.assertFalse(path.exists())

    def test_init_iteration_can_create_benchmark_suite_by_name(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "benchmark-iteration"

            subprocess.run(
                [
                    sys.executable,
                    str(INIT_SCRIPT_PATH),
                    "--suite",
                    "benchmark",
                    "--schema",
                    str(SCHEMA_PATH),
                    "--output",
                    str(output_dir),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertEqual(len(list((output_dir / "baseline").glob("*.prompt.md"))), 24)
            self.assertEqual(len(list((output_dir / "dddjango").glob("*.prompt.md"))), 24)
            self.assertEqual(len(list((output_dir / "answer-key").glob("*.json"))), 24)
            self.assertEqual(len(json.loads((output_dir / "grades.json").read_text())), 48)

    def test_init_iteration_can_create_hard_benchmark_suite_by_name(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "hard-benchmark-iteration"

            subprocess.run(
                [
                    sys.executable,
                    str(INIT_SCRIPT_PATH),
                    "--suite",
                    "hard-benchmark",
                    "--schema",
                    str(SCHEMA_PATH),
                    "--output",
                    str(output_dir),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertEqual(len(list((output_dir / "baseline").glob("*.prompt.md"))), 8)
            self.assertEqual(len(list((output_dir / "dddjango").glob("*.prompt.md"))), 8)
            self.assertEqual(len(list((output_dir / "answer-key").glob("*.json"))), 8)
            self.assertEqual(len(json.loads((output_dir / "grades.json").read_text())), 16)

    def test_init_iteration_can_create_targeted_rerun_suite_by_name(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "targeted-rerun-iteration"

            subprocess.run(
                [
                    sys.executable,
                    str(INIT_SCRIPT_PATH),
                    "--suite",
                    "targeted-rerun",
                    "--schema",
                    str(SCHEMA_PATH),
                    "--output",
                    str(output_dir),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertEqual(len(list((output_dir / "baseline").glob("*.prompt.md"))), 4)
            self.assertEqual(len(list((output_dir / "dddjango").glob("*.prompt.md"))), 4)
            self.assertEqual(len(list((output_dir / "answer-key").glob("*.json"))), 4)
            self.assertEqual(len(json.loads((output_dir / "grades.json").read_text())), 8)

    def test_init_iteration_can_create_conformance_rerun_suite_by_name(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "conformance-rerun-iteration"

            subprocess.run(
                [
                    sys.executable,
                    str(INIT_SCRIPT_PATH),
                    "--suite",
                    "conformance-rerun",
                    "--schema",
                    str(SCHEMA_PATH),
                    "--output",
                    str(output_dir),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertEqual(len(list((output_dir / "baseline").glob("*.prompt.md"))), 5)
            self.assertEqual(len(list((output_dir / "dddjango").glob("*.prompt.md"))), 5)
            self.assertEqual(len(list((output_dir / "answer-key").glob("*.json"))), 5)
            self.assertEqual(len(json.loads((output_dir / "grades.json").read_text())), 10)

    def test_init_iteration_can_create_reference_ceiling_variant_set(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "reference-ceiling-iteration"

            subprocess.run(
                [
                    sys.executable,
                    str(INIT_SCRIPT_PATH),
                    "--suite",
                    "pilot",
                    "--schema",
                    str(SCHEMA_PATH),
                    "--output",
                    str(output_dir),
                    "--variant-set",
                    "reference-ceiling",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertEqual(len(list((output_dir / "baseline").glob("*.prompt.md"))), 8)
            self.assertEqual(len(list((output_dir / "skill-core-only").glob("*.prompt.md"))), 8)
            self.assertEqual(len(list((output_dir / "dddjango").glob("*.prompt.md"))), 8)
            self.assertEqual(len(list((output_dir / "oracle-reference").glob("*.prompt.md"))), 8)
            self.assertEqual(len(json.loads((output_dir / "grades.json").read_text())), 32)

    def test_init_iteration_can_create_plugin_real_variant_set(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "plugin-real-iteration"

            subprocess.run(
                [
                    sys.executable,
                    str(INIT_SCRIPT_PATH),
                    "--suite",
                    "trigger",
                    "--schema",
                    str(SCHEMA_PATH),
                    "--output",
                    str(output_dir),
                    "--variant-set",
                    "plugin-real",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertEqual(len(list((output_dir / "baseline").glob("*.prompt.md"))), 30)
            self.assertEqual(len(list((output_dir / "dddjango-plugin").glob("*.prompt.md"))), 30)
            self.assertEqual(len(json.loads((output_dir / "grades.json").read_text())), 60)

    def test_init_iteration_can_create_trigger_suite_by_name(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "trigger-iteration"

            subprocess.run(
                [
                    sys.executable,
                    str(INIT_SCRIPT_PATH),
                    "--suite",
                    "trigger",
                    "--schema",
                    str(SCHEMA_PATH),
                    "--output",
                    str(output_dir),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            answer_keys = sorted((output_dir / "answer-key").glob("*.json"))
            grades = json.loads((output_dir / "grades.json").read_text())

            self.assertEqual(len(list((output_dir / "baseline").glob("*.prompt.md"))), 30)
            self.assertEqual(len(list((output_dir / "dddjango").glob("*.prompt.md"))), 30)
            self.assertEqual(len(answer_keys), 30)
            self.assertEqual(len(grades), 60)
            self.assertIn(
                "trigger_type",
                json.loads(answer_keys[0].read_text()),
            )
            self.assertIn("trigger", grades[0])

    def test_init_iteration_can_create_real_repo_suite_with_fixture_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "real-repo-iteration"

            subprocess.run(
                [
                    sys.executable,
                    str(INIT_SCRIPT_PATH),
                    "--suite",
                    "real-repo",
                    "--schema",
                    str(SCHEMA_PATH),
                    "--output",
                    str(output_dir),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            prompts = sorted((output_dir / "dddjango").glob("*.prompt.md"))
            answer_keys = sorted((output_dir / "answer-key").glob("*.json"))
            grades = json.loads((output_dir / "grades.json").read_text())
            prompt = (output_dir / "dddjango/real-repo-fat-model-refactor.prompt.md").read_text()
            answer_key = json.loads(
                (output_dir / "answer-key/real-repo-fat-model-refactor.json").read_text()
            )

            self.assertEqual(len(prompts), 6)
            self.assertEqual(len(answer_keys), 6)
            self.assertEqual(len(grades), 12)
            self.assertIn(str(REAL_REPO_FIXTURE_PATH), prompt)
            self.assertIn("unified diff", prompt)
            self.assertEqual(answer_key["fixture"], "evals/fixtures/django-shop")
            self.assertEqual(answer_key["mode"], "forward-diff")

    def test_real_repo_diff_evaluator_extracts_and_applies_unified_diff(self):
        module = load_module(REAL_REPO_DIFF_SCRIPT_PATH)
        output = """제안 diff입니다.

```diff
diff --git a/app/models.py b/app/models.py
index 83db48f..f735c2d 100644
--- a/app/models.py
+++ b/app/models.py
@@ -1 +1,2 @@
 name = "before"
+status = "after"
```
"""

        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "fixture"
            (fixture / "app").mkdir(parents=True)
            (fixture / "app/models.py").write_text('name = "before"\n')
            workspace = Path(temp_dir) / "workspace"

            result = module.evaluate_output_diff(
                output,
                fixture_path=fixture,
                workspace_path=workspace,
                run_checks=False,
            )

            self.assertTrue(result["diff_found"])
            self.assertEqual(result["patch_check"], "passed")
            self.assertEqual(result["patch_applied"], "passed")
            self.assertIn('status = "after"', (workspace / "app/models.py").read_text())

    def test_real_repo_diff_evaluator_writes_summary_and_report_section(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            fixture = root / "fixture"
            (fixture / "app").mkdir(parents=True)
            (fixture / "app/models.py").write_text('name = "before"\n')

            iteration = root / "iteration"
            (iteration / "baseline").mkdir(parents=True)
            (iteration / "dddjango").mkdir()
            (iteration / "answer-key").mkdir()
            answer_key = {
                "case_id": "real-repo-case",
                "title": "Real repo case",
                "category": "real-repo",
                "expectations": ["real_repo_applicability"],
                "scoring_focus": ["patch applies"],
                "fixture": "fixture",
                "mode": "forward-diff",
            }
            (iteration / "answer-key/real-repo-case.json").write_text(
                json.dumps(answer_key) + "\n"
            )
            output = """```diff
diff --git a/app/models.py b/app/models.py
index 83db48f..f735c2d 100644
--- a/app/models.py
+++ b/app/models.py
@@ -1 +1,2 @@
 name = "before"
+status = "after"
```
"""
            (iteration / "baseline/real-repo-case.output.md").write_text(output)
            (iteration / "dddjango/real-repo-case.output.md").write_text(output)
            (iteration / "grades.json").write_text(
                json.dumps(
                    [
                        {
                            "case_id": "real-repo-case",
                            "variant": "baseline",
                            "scores": {criterion: 1 for criterion in [
                                "domain_fit",
                                "django_ninja_compliance",
                                "actionability",
                                "architecture_quality",
                                "testing_quality",
                                "korean_first",
                                "conciseness",
                                "safety",
                            ]},
                            "flags": {},
                        },
                        {
                            "case_id": "real-repo-case",
                            "variant": "dddjango",
                            "scores": {criterion: 2 for criterion in [
                                "domain_fit",
                                "django_ninja_compliance",
                                "actionability",
                                "architecture_quality",
                                "testing_quality",
                                "korean_first",
                                "conciseness",
                                "safety",
                            ]},
                            "flags": {},
                        },
                    ]
                )
                + "\n"
            )
            (iteration / "timing.json").write_text(
                json.dumps(
                    [
                        {"case_id": "real-repo-case", "variant": "baseline", "duration_sec": 1, "returncode": 0},
                        {"case_id": "real-repo-case", "variant": "dddjango", "duration_sec": 1, "returncode": 0},
                    ]
                )
                + "\n"
            )

            subprocess.run(
                [
                    sys.executable,
                    str(REAL_REPO_DIFF_SCRIPT_PATH),
                    str(iteration),
                    "--root",
                    str(root),
                    "--skip-checks",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                [
                    sys.executable,
                    str(REPORT_SCRIPT_PATH),
                    str(iteration),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            summary = json.loads((iteration / "real_repo_evaluation.json").read_text())
            html = (iteration / "report.html").read_text()

            self.assertEqual(summary["summary"]["dddjango"]["patch_applied"], 1)
            self.assertIn("Real Repo Patch Evaluation", html)
            self.assertIn("real-repo-case", html)
            self.assertIn("PATCH PASS", html)

    def test_render_report_includes_conformance_summary_when_available(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            iteration = Path(temp_dir) / "iteration"
            (iteration / "baseline").mkdir(parents=True)
            (iteration / "dddjango").mkdir()
            (iteration / "answer-key").mkdir()
            answer_key = {
                "id": "api-case",
                "title": "API case",
                "category": "api-design",
                "expectations": ["korean_first", "django_ninja_compliance"],
            }
            (iteration / "answer-key/api-case.json").write_text(
                json.dumps(answer_key, ensure_ascii=False) + "\n"
            )
            (iteration / "baseline/api-case.output.md").write_text("plain answer\n")
            (iteration / "dddjango/api-case.output.md").write_text("Django Ninja Router와 Schema\n")
            score_fields = {
                "domain_fit": 10,
                "django_ninja_compliance": 10,
                "actionability": 10,
                "architecture_quality": 10,
                "testing_quality": 10,
                "korean_first": 10,
                "conciseness": 10,
                "safety": 10,
            }
            (iteration / "grades.json").write_text(
                json.dumps(
                    [
                        {
                            "case_id": "api-case",
                            "variant": "baseline",
                            "scores": score_fields,
                            "flags": {},
                        },
                        {
                            "case_id": "api-case",
                            "variant": "dddjango",
                            "scores": score_fields,
                            "flags": {},
                        },
                    ],
                    ensure_ascii=False,
                )
                + "\n"
            )
            (iteration / "timing.json").write_text(
                json.dumps(
                    [
                        {"case_id": "api-case", "variant": "baseline", "duration_sec": 1, "returncode": 0},
                        {"case_id": "api-case", "variant": "dddjango", "duration_sec": 1, "returncode": 1},
                    ]
                )
                + "\n"
            )
            (iteration / "conformance.json").write_text(
                json.dumps(
                    {
                        "version": 1,
                        "summary": {
                            "baseline_avg_conformance": 10,
                            "dddjango_avg_conformance": 90,
                            "delta": 80,
                            "dddjango_required_rule_pass_rate": 95,
                            "critical_violations": 0,
                            "forbidden_pattern_count": 0,
                            "release_gate": {
                                "dddjango_conformance_score": {
                                    "passed": True,
                                    "value": 90,
                                    "required": 85,
                                }
                            },
                        },
                        "cases": [
                            {
                                "case_id": "api-case",
                                "variant": "baseline",
                                "category": "api-design",
                                "conformance_score": 10,
                                "required_rule_pass_rate": 10,
                                "passed_rules": [],
                                "failed_rules": ["uses_django_ninja_router"],
                                "critical_violations": ["uses_django_ninja_router"],
                                "forbidden_patterns": [],
                            },
                            {
                                "case_id": "api-case",
                                "variant": "dddjango",
                                "category": "api-design",
                                "conformance_score": 90,
                                "required_rule_pass_rate": 95,
                                "passed_rules": ["uses_django_ninja_router"],
                                "failed_rules": [],
                                "critical_violations": [],
                                "forbidden_patterns": [],
                            },
                        ],
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

            subprocess.run(
                [
                    sys.executable,
                    str(REPORT_SCRIPT_PATH),
                    str(iteration),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            html = (iteration / "report.html").read_text()
            self.assertIn("dddjango Convention Conformance", html)
            self.assertIn("Convention Score", html)
            self.assertIn("uses_django_ninja_router", html)

    def test_run_prompts_extracts_prompt_and_builds_isolated_baseline_command(self):
        module = load_module(RUN_SCRIPT_PATH)
        text = (
            "# pilot-negative-drf\n\n"
            "Variant: baseline\n"
            "Category: negative-control\n\n"
            "## Prompt\n\n"
            "DRF ViewSet으로 상품 API 만들어줘.\n"
        )

        self.assertEqual(
            module.extract_prompt(text),
            "DRF ViewSet으로 상품 API 만들어줘.",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            prompt_file = Path(temp_dir) / "baseline/pilot-negative-drf.prompt.md"
            prompt_file.parent.mkdir()
            prompt_file.write_text(text)

            command = module.build_codex_command(
                prompt_file=prompt_file,
                output_file=Path("baseline/pilot-negative-drf.output.md"),
                cwd=Path("/tmp/dddjango-eval"),
                variant="baseline",
                model="gpt-5.4",
                profile="",
                ignore_user_config=True,
            )

        self.assertIn("--ignore-user-config", command)
        self.assertIn("--ephemeral", command)
        self.assertIn("--skip-git-repo-check", command)
        self.assertIn("--cd", command)
        self.assertIn("/tmp/dddjango-eval", command)
        self.assertIn("-m", command)
        self.assertIn("gpt-5.4", command)
        self.assertNotIn("Variant: baseline", " ".join(command))
        self.assertFalse(
            any(part.startswith("developer_instructions=") for part in command)
        )

    def test_run_prompts_can_inject_local_dddjango_skill_instructions(self):
        module = load_module(RUN_SCRIPT_PATH)

        instructions = module.dddjango_developer_instructions(ROOT)
        self.assertIn(str(ROOT / "skills"), instructions)
        self.assertIn("Django Ninja Schema/Router", instructions)
        self.assertIn("RED pytest examples", instructions)

        with tempfile.TemporaryDirectory() as temp_dir:
            prompt_file = Path(temp_dir) / "dddjango/pilot-negative-drf.prompt.md"
            prompt_file.parent.mkdir()
            prompt_file.write_text("## Prompt\n\nDRF ViewSet으로 상품 API 만들어줘.\n")

            command = module.build_codex_command(
                prompt_file=prompt_file,
                output_file=Path("dddjango/pilot-negative-drf.output.md"),
                cwd=Path("/tmp/dddjango-eval"),
                variant="dddjango",
                model="",
                profile="",
                ignore_user_config=False,
                developer_instructions=instructions,
            )

        self.assertIn("-c", command)
        self.assertTrue(
            any(part.startswith("developer_instructions=") for part in command)
        )
        self.assertIn("DRF ViewSet으로 상품 API 만들어줘.", command[-1])

    def test_run_prompts_scopes_dddjango_skill_instructions_by_case(self):
        module = load_module(RUN_SCRIPT_PATH)

        negative_drf = module.dddjango_developer_instructions(
            ROOT,
            case_id="pilot-negative-drf",
        )
        tdd_coupon = module.dddjango_developer_instructions(
            ROOT,
            case_id="pilot-tdd-coupon",
        )

        self.assertIn("implementation-django-ninja/SKILL.md", negative_drf)
        self.assertNotIn("implementation-tdd/SKILL.md", negative_drf)
        self.assertNotIn("For pytest/TDD", negative_drf)
        self.assertIn("implementation-tdd/SKILL.md", tdd_coupon)
        self.assertIn("implementation-test/SKILL.md", tdd_coupon)
        self.assertIn("For pytest/TDD", tdd_coupon)
        self.assertLess(len(negative_drf), len(module.dddjango_developer_instructions(ROOT)))

        api_standard = module.dddjango_developer_instructions(
            ROOT,
            case_id="pilot-api-standard",
        )
        db_orders = module.dddjango_developer_instructions(
            ROOT,
            case_id="pilot-db-orders",
        )
        review_view_logic = module.dddjango_developer_instructions(
            ROOT,
            case_id="pilot-review-view-logic",
        )

        self.assertIn("architecture-api/SKILL.md", api_standard)
        self.assertIn("implementation-django-ninja/SKILL.md", api_standard)
        self.assertIn("architecture-db/SKILL.md", db_orders)
        self.assertIn("implementation-django/SKILL.md", db_orders)
        self.assertIn("implementation-django-ninja/SKILL.md", review_view_logic)
        self.assertNotIn("copyable team standard", api_standard)
        self.assertNotIn("constraints, indexes, locking", db_orders)
        self.assertNotIn("thin Ninja endpoint", review_view_logic)
        self.assertNotIn("For pytest/TDD", api_standard)
        self.assertNotIn("For pytest/TDD", db_orders)

        review_fat_model = module.dddjango_developer_instructions(
            ROOT,
            case_id="pilot-review-fat-model",
        )
        self.assertIn("implementation-cleancode/SKILL.md", review_fat_model)
        self.assertNotIn("severity-ranked findings", review_fat_model)
        self.assertNotIn("assertNumQueries", review_fat_model)

        api_order = module.dddjango_developer_instructions(
            ROOT,
            case_id="pilot-api-order-create",
        )
        implementation_coupon = module.dddjango_developer_instructions(
            ROOT,
            case_id="pilot-implementation-coupon",
        )

        for instructions in [api_order, implementation_coupon]:
            self.assertNotIn("Keep under 900 words", instructions)
            self.assertNotIn("no full domain model", instructions)
            self.assertNotIn("only critical code", instructions)

        self.assertNotIn("Keep under 700 words", implementation_coupon)
        self.assertNotIn("architecture-implementation-patterns/SKILL.md", implementation_coupon)

    def test_run_prompts_scopes_benchmark_and_trigger_cases_from_answer_key(self):
        module = load_module(RUN_SCRIPT_PATH)

        api_case = {
            "category": "api-design",
            "prompt": "주문 상태 변경 API를 Django Ninja와 DDD 기준으로 설계해줘.",
            "expectations": [
                "korean_first",
                "django_ninja_compliance",
                "ddd_boundaries",
                "transaction_boundary",
            ],
            "scoring_focus": ["Django Ninja Router와 Schema를 사용한다."],
        }
        api_instructions = module.dddjango_developer_instructions(
            ROOT,
            case_id="benchmark-api-order-status",
            case=api_case,
        )

        self.assertIn("architecture-api/SKILL.md", api_instructions)
        self.assertIn("architecture-ddd/SKILL.md", api_instructions)
        self.assertIn("implementation-django-ninja/SKILL.md", api_instructions)
        self.assertIn("Read only", api_instructions)
        self.assertIn("request: HttpRequest", api_instructions)
        self.assertIn("explicit return type", api_instructions)
        self.assertIn("Keep the answer focused", api_instructions)
        self.assertNotIn("Focus on:", api_instructions)
        self.assertNotIn("Django Ninja Router와 Schema를 사용한다.", api_instructions)
        self.assertLess(len(api_instructions), len(module.dddjango_developer_instructions(ROOT)))

        negative_trigger = {
            "category": "trigger",
            "trigger_type": "negative",
            "prompt": "Rust로 문자열 slugify 함수를 작성해줘.",
            "expectations": ["korean_first"],
            "scoring_focus": ["Rust 코드만 제공한다."],
        }
        negative_instructions = module.dddjango_developer_instructions(
            ROOT,
            case_id="trigger-negative-rust-function",
            case=negative_trigger,
        )
        self.assertEqual(negative_instructions, "")

        conflict_trigger = {
            "category": "trigger",
            "trigger_type": "conflict",
            "prompt": "DRF ViewSet과 ModelSerializer로 상품 API를 작성해줘.",
            "expectations": ["korean_first", "reject_drf"],
            "scoring_focus": ["DRF 코드를 생성하지 않는다."],
        }
        conflict_instructions = module.dddjango_developer_instructions(
            ROOT,
            case_id="trigger-conflict-drf-viewset",
            case=conflict_trigger,
        )

        self.assertIn("implementation-django-ninja/SKILL.md", conflict_instructions)
        self.assertIn("produce no DRF code", conflict_instructions)
        self.assertNotIn("Focus on:", conflict_instructions)

        ambiguous_trigger = {
            "category": "trigger",
            "trigger_type": "ambiguous",
            "prompt": "서비스 레이어를 어디에 두는 게 좋을까?",
            "expectations": ["korean_first", "ambiguous_handling"],
            "scoring_focus": ["조건부로 답한다."],
        }
        ambiguous_instructions = module.dddjango_developer_instructions(
            ROOT,
            case_id="trigger-ambiguous-service-layer",
            case=ambiguous_trigger,
        )

        self.assertIn(
            "architecture-implementation-patterns/SKILL.md",
            ambiguous_instructions,
        )
        self.assertIn("implementation-django/SKILL.md", ambiguous_instructions)
        self.assertIn("Keep the answer focused", ambiguous_instructions)
        self.assertNotIn("맥락이 불명확합니다", ambiguous_instructions)

        legacy_conflict = module.dddjango_developer_instructions(
            ROOT,
            case_id="trigger-conflict-drf-viewset",
            case=conflict_trigger,
            allow_generation_hints=True,
        )
        legacy_ambiguous = module.dddjango_developer_instructions(
            ROOT,
            case_id="trigger-ambiguous-service-layer",
            case=ambiguous_trigger,
            allow_generation_hints=True,
        )

        self.assertIn("Do not output DRF implementation code", legacy_conflict)
        self.assertIn("맥락이 불명확합니다", legacy_ambiguous)

    def test_run_prompts_builds_reference_ceiling_instructions(self):
        module = load_module(RUN_SCRIPT_PATH)
        case = {
            "case_id": "benchmark-api-product-search",
            "category": "api-design",
            "prompt": "상품 검색 API를 Django Ninja 기준으로 설계해줘.",
            "expectations": ["korean_first", "django_ninja_compliance", "api_standard"],
            "scoring_focus": ["검색 필터와 페이지네이션 표준을 제시한다."],
        }

        core = module.developer_instructions_for_variant(
            ROOT,
            "skill-core-only",
            "benchmark-api-product-search",
            case,
        )
        oracle = module.developer_instructions_for_variant(
            ROOT,
            "oracle-reference",
            "benchmark-api-product-search",
            case,
        )

        self.assertIn("SKILL.md only", core)
        self.assertIn("Do not open references/", core)
        self.assertIn("implementation-django-ninja/SKILL.md", core)
        self.assertNotIn("response-pagination.md", core)

        self.assertIn("reference-ceiling oracle", oracle)
        self.assertIn("response-pagination.md", oracle)
        self.assertIn("input-filtering.md", oracle)
        self.assertIn("Do not use answer keys", oracle)
        self.assertNotIn("answer-key", oracle)

    def test_run_prompts_does_not_inject_local_skills_for_plugin_real_variant(self):
        module = load_module(RUN_SCRIPT_PATH)
        case = {
            "case_id": "trigger-positive-ninja-order-api",
            "category": "trigger",
            "trigger_type": "positive",
            "prompt": "Django Ninja로 주문 생성 API를 설계해줘.",
            "expectations": ["korean_first", "django_ninja_compliance"],
            "scoring_focus": ["Django Ninja Router를 사용한다."],
        }

        instructions = module.developer_instructions_for_variant(
            ROOT,
            "dddjango-plugin",
            "trigger-positive-ninja-order-api",
            case,
        )

        self.assertEqual(instructions, "")

    def test_run_prompts_loads_answer_keys_for_iteration_metadata(self):
        module = load_module(RUN_SCRIPT_PATH)

        with tempfile.TemporaryDirectory() as temp_dir:
            iteration = Path(temp_dir)
            (iteration / "answer-key").mkdir()
            (iteration / "answer-key/case-a.json").write_text(
                json.dumps({"case_id": "case-a", "category": "api-design"}) + "\n"
            )

            cases = module.load_answer_keys(iteration)

            self.assertEqual(cases["case-a"]["category"], "api-design")

    def test_run_prompts_isolates_non_triggering_dddjango_cases_from_user_config(self):
        module = load_module(RUN_SCRIPT_PATH)

        with tempfile.TemporaryDirectory() as temp_dir:
            iteration = Path(temp_dir) / "iteration"
            (iteration / "dddjango").mkdir(parents=True)
            (iteration / "answer-key").mkdir()
            (iteration / "dddjango/trigger-negative-rust-function.prompt.md").write_text(
                "## Prompt\n\nRust로 문자열 slugify 함수를 작성해줘.\n"
            )
            (iteration / "timing.json").write_text("[]\n")
            (iteration / "answer-key/trigger-negative-rust-function.json").write_text(
                json.dumps(
                    {
                        "category": "trigger",
                        "trigger_type": "negative",
                        "prompt": "Rust로 문자열 slugify 함수를 작성해줘.",
                        "expectations": ["korean_first"],
                        "scoring_focus": ["Rust 코드만 제공한다."],
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

            args = type(
                "Args",
                (),
                {
                    "iteration": str(iteration),
                    "variant": "dddjango",
                    "case": "trigger-negative-rust-function",
                    "cwd": str(Path(temp_dir) / "cwd"),
                    "ignore_user_config": False,
                    "allow_user_config": False,
                    "model": "",
                    "profile": "",
                    "root": str(ROOT),
                    "use_local_dddjango_skills": True,
                    "dry_run": True,
                    "keep_going": False,
                },
            )()

            commands = []
            original_build = module.build_codex_command

            def capture_command(**kwargs):
                command = original_build(**kwargs)
                commands.append(command)
                return command

            module.build_codex_command = capture_command
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    module.run_variant(args)
            finally:
                module.build_codex_command = original_build

            self.assertEqual(len(commands), 1)
            self.assertIn("--ignore-user-config", commands[0])
            developer_instruction_args = [
                part for part in commands[0] if part.startswith("developer_instructions=")
            ]
            self.assertEqual(developer_instruction_args, [])

    def test_run_prompts_records_timeout_and_keeps_going(self):
        module = load_module(RUN_SCRIPT_PATH)

        with tempfile.TemporaryDirectory() as temp_dir:
            iteration = Path(temp_dir) / "iteration"
            (iteration / "baseline").mkdir(parents=True)
            (iteration / "answer-key").mkdir()
            (iteration / "baseline/case-a.prompt.md").write_text(
                "## Prompt\n\nDjango Ninja API를 설계해줘.\n"
            )
            (iteration / "timing.json").write_text("[]\n")
            (iteration / "answer-key/case-a.json").write_text(
                json.dumps({"category": "api-design", "prompt": "Django Ninja API"})
                + "\n"
            )

            args = type(
                "Args",
                (),
                {
                    "iteration": str(iteration),
                    "variant": "baseline",
                    "case": "",
                    "cwd": str(Path(temp_dir) / "cwd"),
                    "ignore_user_config": False,
                    "allow_user_config": False,
                    "model": "",
                    "profile": "",
                    "root": str(ROOT),
                    "use_local_dddjango_skills": True,
                    "dry_run": False,
                    "keep_going": True,
                    "timeout_sec": 1,
                },
            )()

            original_run = module.subprocess.run

            def timeout_run(command, **kwargs):
                raise subprocess.TimeoutExpired(
                    command,
                    timeout=kwargs["timeout"],
                    output="partial stdout",
                    stderr="partial stderr",
                )

            module.subprocess.run = timeout_run
            try:
                with contextlib.redirect_stdout(io.StringIO()) as stdout:
                    module.run_variant(args)
            finally:
                module.subprocess.run = original_run

            timing = json.loads((iteration / "timing.json").read_text())
            output = (iteration / "baseline/case-a.output.md").read_text()
            log = (iteration / "baseline/case-a.codex.log").read_text()

            self.assertEqual(timing[0]["returncode"], 124)
            self.assertIn("timeout after 1s", stdout.getvalue())
            self.assertIn("timed out", output)
            self.assertIn("partial stdout", log)
            self.assertIn("partial stderr", log)

    def test_render_report_creates_html_comparison_dashboard(self):
        module = load_module(REPORT_SCRIPT_PATH)

        with tempfile.TemporaryDirectory() as temp_dir:
            iteration = Path(temp_dir)
            (iteration / "baseline").mkdir()
            (iteration / "skill-core-only").mkdir()
            (iteration / "dddjango").mkdir()
            (iteration / "oracle-reference").mkdir()
            (iteration / "answer-key").mkdir()
            (iteration / "baseline/case-a.output.md").write_text(
                "# Baseline Output\n\n- **plain** `result`\n"
            )
            (iteration / "skill-core-only/case-a.output.md").write_text(
                "# Core Only Output\n\nSKILL.md만 사용한 결과입니다.\n"
            )
            (iteration / "dddjango/case-a.output.md").write_text(
                "# dddjango Output\n\n```python\nprint('ok')\n```\n"
            )
            (iteration / "oracle-reference/case-a.output.md").write_text(
                "# Oracle Reference Output\n\nreference를 직접 사용한 결과입니다.\n"
            )
            (iteration / "answer-key/case-a.json").write_text(
                json.dumps(
                    {
                        "title": "Case A title",
                        "category": "api-design",
                        "expectations": ["korean_first", "django_ninja_compliance"],
                    },
                    ensure_ascii=False,
                )
            )
            (iteration / "grades.json").write_text(
                json.dumps(
                    [
                        {
                            "case_id": "case-a",
                            "variant": "baseline",
                            "scores": {
                                "domain_fit": 10,
                                "django_ninja_compliance": 20,
                                "actionability": 10,
                                "architecture_quality": 10,
                                "testing_quality": 5,
                                "korean_first": 10,
                                "conciseness": 5,
                                "safety": 5,
                            },
                            "notes": "baseline note",
                            "usability": {
                                "actionable": 3,
                                "concise": 4,
                                "realistic_file_layout": 3,
                                "korean_quality": 5,
                                "notes": "baseline usable",
                            },
                            "flags": {
                                "korean_first": True,
                                "django_ninja_used": True,
                                "drf_endorsed": False,
                                "negative_control_passed": False,
                            },
                        },
                        {
                            "case_id": "case-a",
                            "variant": "skill-core-only",
                            "scores": {
                                "domain_fit": 12,
                                "django_ninja_compliance": 20,
                                "actionability": 10,
                                "architecture_quality": 10,
                                "testing_quality": 5,
                                "korean_first": 10,
                                "conciseness": 5,
                                "safety": 5,
                            },
                            "notes": "core note",
                            "usability": {
                                "actionable": 4,
                                "concise": 4,
                                "realistic_file_layout": 3,
                                "korean_quality": 5,
                                "notes": "core usable",
                            },
                            "flags": {
                                "korean_first": True,
                                "django_ninja_used": True,
                                "drf_endorsed": False,
                                "negative_control_passed": False,
                            },
                        },
                        {
                            "case_id": "case-a",
                            "variant": "dddjango",
                            "scores": {
                                "domain_fit": 15,
                                "django_ninja_compliance": 20,
                                "actionability": 12,
                                "architecture_quality": 12,
                                "testing_quality": 7,
                                "korean_first": 10,
                                "conciseness": 4,
                                "safety": 5,
                            },
                            "notes": "dddjango note",
                            "usability": {
                                "actionable": 5,
                                "concise": 4,
                                "realistic_file_layout": 5,
                                "korean_quality": 5,
                                "notes": "바로 적용 가능",
                            },
                            "flags": {
                                "korean_first": True,
                                "django_ninja_used": True,
                                "drf_endorsed": False,
                                "negative_control_passed": False,
                            },
                        },
                        {
                            "case_id": "case-a",
                            "variant": "oracle-reference",
                            "scores": {
                                "domain_fit": 18,
                                "django_ninja_compliance": 20,
                                "actionability": 14,
                                "architecture_quality": 14,
                                "testing_quality": 7,
                                "korean_first": 10,
                                "conciseness": 4,
                                "safety": 5,
                            },
                            "notes": "oracle note",
                            "usability": {
                                "actionable": 5,
                                "concise": 4,
                                "realistic_file_layout": 5,
                                "korean_quality": 5,
                                "notes": "oracle usable",
                            },
                            "flags": {
                                "korean_first": True,
                                "django_ninja_used": True,
                                "drf_endorsed": False,
                                "negative_control_passed": False,
                            },
                        },
                    ],
                    ensure_ascii=False,
                )
                + "\n"
            )
            (iteration / "timing.json").write_text(
                json.dumps(
                    [
                        {
                            "case_id": "case-a",
                            "variant": "baseline",
                            "duration_sec": 10.0,
                        },
                        {
                            "case_id": "case-a",
                            "variant": "skill-core-only",
                            "duration_sec": 11.0,
                        },
                        {
                            "case_id": "case-a",
                            "variant": "dddjango",
                            "duration_sec": 12.0,
                        },
                        {
                            "case_id": "case-a",
                            "variant": "oracle-reference",
                            "duration_sec": 13.0,
                        },
                    ]
                )
                + "\n"
            )

            report_path = module.render_report(iteration)
            html = report_path.read_text()

            self.assertIn("dddjango Codex Evaluation Report", html)
            self.assertIn("Baseline Score", html)
            self.assertIn("dddjango Score", html)
            self.assertIn("Release Gate", html)
            self.assertIn("Overall Lift", html)
            self.assertIn("Quality Gate Lift", html)
            self.assertIn("headroom", html)
            self.assertIn("pts", html)
            self.assertIn("Usability Summary", html)
            self.assertIn("Realistic Layout", html)
            self.assertIn("Korean Quality", html)
            self.assertIn("바로 적용 가능", html)
            self.assertIn("Case Comparison: Without Skill vs With dddjango", html)
            self.assertIn("Reference Ceiling Comparison", html)
            self.assertIn("Core Only", html)
            self.assertIn("Oracle Reference", html)
            self.assertIn("Reference Contribution", html)
            self.assertIn("Ceiling Gap", html)
            self.assertIn("Completed Cases", html)
            self.assertIn("Case A title", html)
            self.assertIn("api-design", html)
            self.assertIn("korean_first, django_ninja_compliance", html)
            self.assertIn("Without Skill", html)
            self.assertIn("With dddjango", html)
            self.assertIn("+10.0", html)
            self.assertNotIn("file://", html)
            self.assertIn('href="artifacts/case-a-baseline.html"', html)
            self.assertIn('href="artifacts/case-a-skill-core-only.html"', html)
            self.assertIn('href="artifacts/case-a-dddjango.html"', html)
            self.assertIn('href="artifacts/case-a-oracle-reference.html"', html)
            self.assertIn('href="artifacts/case-a-answer-key.html"', html)

            baseline_artifact = iteration / "artifacts/case-a-baseline.html"
            core_artifact = iteration / "artifacts/case-a-skill-core-only.html"
            dddjango_artifact = iteration / "artifacts/case-a-dddjango.html"
            oracle_artifact = iteration / "artifacts/case-a-oracle-reference.html"
            answer_key_artifact = iteration / "artifacts/case-a-answer-key.html"
            self.assertTrue(baseline_artifact.exists())
            self.assertTrue(core_artifact.exists())
            self.assertTrue(dddjango_artifact.exists())
            self.assertTrue(oracle_artifact.exists())
            self.assertTrue(answer_key_artifact.exists())
            self.assertIn("<h1>Baseline Output</h1>", baseline_artifact.read_text())
            self.assertIn("<li><strong>plain</strong> <code>result</code></li>", baseline_artifact.read_text())
            self.assertIn("<h1>dddjango Output</h1>", dddjango_artifact.read_text())
            self.assertIn("<pre><code>", dddjango_artifact.read_text())
            self.assertIn("print(&#x27;ok&#x27;)", dddjango_artifact.read_text())
            self.assertIn("Case A title", answer_key_artifact.read_text())

    def test_render_repeat_summary_compares_iterations_in_html(self):
        module = load_module(REPEAT_REPORT_SCRIPT_PATH)

        def scores_for_total(total):
            base = total // len(module.CRITERIA)
            scores = {criterion: base for criterion in module.CRITERIA}
            scores[module.CRITERIA[0]] += total - base * len(module.CRITERIA)
            return scores

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for index, baseline_score, dddjango_score in [
                (1, 80, 90),
                (2, 82, 88),
            ]:
                iteration = root / f"benchmark-{index}"
                (iteration / "answer-key").mkdir(parents=True)
                (iteration / "answer-key/case-a.json").write_text(
                    json.dumps({"title": "Case A", "category": "api-design"})
                    + "\n"
                )
                (iteration / "grades.json").write_text(
                    json.dumps(
                        [
                            {
                                "case_id": "case-a",
                                "variant": "baseline",
                                "scores": scores_for_total(baseline_score),
                                "flags": {},
                            },
                            {
                                "case_id": "case-a",
                                "variant": "dddjango",
                                "scores": scores_for_total(dddjango_score),
                                "flags": {},
                            },
                        ]
                    )
                    + "\n"
                )
                (iteration / "timing.json").write_text(
                    json.dumps(
                        [
                            {
                                "case_id": "case-a",
                                "variant": "baseline",
                                "duration_sec": 10 + index,
                                "returncode": 0,
                            },
                            {
                                "case_id": "case-a",
                                "variant": "dddjango",
                                "duration_sec": 12 + index,
                                "returncode": 0,
                            },
                        ]
                    )
                    + "\n"
                )

            output = root / "summary/report.html"
            summary = module.render_repeat_summary(
                [root / "benchmark-1", root / "benchmark-2"],
                output,
                title="Benchmark Repeat Summary",
            )
            html = output.read_text()

            self.assertEqual(summary["overall"]["baseline_avg"], 81.0)
            self.assertEqual(summary["overall"]["dddjango_avg"], 89.0)
            self.assertIn("Benchmark Repeat Summary", html)
            self.assertIn("benchmark-1", html)
            self.assertIn("api-design", html)
            self.assertIn("+8.00", html)

    def test_render_report_includes_trigger_matrix_and_gates(self):
        module = load_module(REPORT_SCRIPT_PATH)

        with tempfile.TemporaryDirectory() as temp_dir:
            iteration = Path(temp_dir)
            (iteration / "baseline").mkdir()
            (iteration / "dddjango").mkdir()
            (iteration / "answer-key").mkdir()
            for case_id in ["trigger-positive", "trigger-negative"]:
                (iteration / f"baseline/{case_id}.output.md").write_text("baseline")
                (iteration / f"dddjango/{case_id}.output.md").write_text("dddjango")
            (iteration / "answer-key/trigger-positive.json").write_text(
                json.dumps(
                    {
                        "title": "Positive trigger",
                        "category": "trigger",
                        "expectations": ["korean_first"],
                        "trigger_type": "positive",
                        "expected_behavior": "Apply dddjango Django Ninja guidance.",
                    },
                    ensure_ascii=False,
                )
            )
            (iteration / "answer-key/trigger-negative.json").write_text(
                json.dumps(
                    {
                        "title": "Negative trigger",
                        "category": "trigger",
                        "expectations": ["korean_first"],
                        "trigger_type": "negative",
                        "expected_behavior": "Do not force Django guidance.",
                    },
                    ensure_ascii=False,
                )
            )
            scores = {
                "domain_fit": 10,
                "django_ninja_compliance": 10,
                "actionability": 10,
                "architecture_quality": 10,
                "testing_quality": 5,
                "korean_first": 10,
                "conciseness": 5,
                "safety": 5,
            }
            flags = {
                "korean_first": True,
                "django_ninja_used": False,
                "drf_endorsed": False,
                "negative_control_passed": True,
            }
            grades = []
            for case_id, trigger_type, observed in [
                ("trigger-positive", "positive", "used dddjango guidance"),
                ("trigger-negative", "negative", "respected FastAPI request"),
            ]:
                grades.extend(
                    [
                        {
                            "case_id": case_id,
                            "variant": "baseline",
                            "scores": scores,
                            "flags": flags,
                            "trigger": {
                                "type": trigger_type,
                                "observed": "baseline",
                                "passed": True,
                            },
                        },
                        {
                            "case_id": case_id,
                            "variant": "dddjango",
                            "scores": scores,
                            "flags": flags,
                            "trigger": {
                                "type": trigger_type,
                                "observed": observed,
                                "passed": True,
                            },
                        },
                    ]
                )
            (iteration / "grades.json").write_text(json.dumps(grades, ensure_ascii=False) + "\n")
            (iteration / "timing.json").write_text(
                json.dumps(
                    [
                        {"case_id": "trigger-positive", "variant": "baseline", "duration_sec": 10},
                        {"case_id": "trigger-positive", "variant": "dddjango", "duration_sec": 11},
                        {"case_id": "trigger-negative", "variant": "baseline", "duration_sec": 10},
                        {"case_id": "trigger-negative", "variant": "dddjango", "duration_sec": 11},
                    ]
                )
                + "\n"
            )

            report_path = module.render_report(iteration)
            html = report_path.read_text()

            self.assertIn("Trigger Matrix", html)
            self.assertIn("Trigger Recall", html)
            self.assertIn("Trigger Precision", html)
            self.assertIn("Positive trigger", html)
            self.assertIn("Negative trigger", html)
            self.assertIn("Apply dddjango Django Ninja guidance.", html)
            self.assertIn("Do not force Django guidance.", html)

    def test_render_report_marks_ninja_gate_not_applicable_without_api_cases(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            iteration = Path(temp_dir)
            (iteration / "baseline").mkdir()
            (iteration / "dddjango").mkdir()
            (iteration / "answer-key").mkdir()
            (iteration / "baseline/case-a.output.md").write_text("baseline")
            (iteration / "dddjango/case-a.output.md").write_text("dddjango")
            (iteration / "answer-key/case-a.json").write_text(
                json.dumps(
                    {
                        "title": "Clean code case",
                        "category": "clean-code",
                        "expectations": ["korean_first", "clean_code"],
                    },
                    ensure_ascii=False,
                )
            )
            scores = {
                "domain_fit": 10,
                "django_ninja_compliance": 10,
                "actionability": 10,
                "architecture_quality": 10,
                "testing_quality": 5,
                "korean_first": 10,
                "conciseness": 5,
                "safety": 5,
            }
            flags = {
                "korean_first": True,
                "django_ninja_used": False,
                "drf_endorsed": False,
                "negative_control_passed": False,
            }
            (iteration / "grades.json").write_text(
                json.dumps(
                    [
                        {
                            "case_id": "case-a",
                            "variant": "baseline",
                            "scores": scores,
                            "flags": flags,
                        },
                        {
                            "case_id": "case-a",
                            "variant": "dddjango",
                            "scores": scores,
                            "flags": flags,
                        },
                    ],
                    ensure_ascii=False,
                )
                + "\n"
            )
            (iteration / "timing.json").write_text(
                json.dumps(
                    [
                        {"case_id": "case-a", "variant": "baseline", "duration_sec": 10},
                        {"case_id": "case-a", "variant": "dddjango", "duration_sec": 10},
                    ]
                )
                + "\n"
            )

            report_path = load_module(REPORT_SCRIPT_PATH).render_report(iteration)
            html = report_path.read_text()

            self.assertIn("Django Ninja compliance", html)
            self.assertIn("N/A", html)
            self.assertIn("no applicable cases", html)


if __name__ == "__main__":
    unittest.main()
