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
TRIGGER_CASES_PATH = ROOT / "evals/shared/cases/trigger.jsonl"
SCHEMA_PATH = ROOT / "evals/codex/rubrics/grading-schema.json"
USABILITY_CHECKLIST_PATH = ROOT / "evals/shared/rubrics/usability-checklist.md"
GRADE_SCRIPT_PATH = ROOT / "evals/codex/scripts/grade_outputs.py"
AUTO_GRADE_SCRIPT_PATH = ROOT / "evals/codex/scripts/auto_grade_outputs.py"
INIT_SCRIPT_PATH = ROOT / "evals/codex/scripts/init_iteration.py"
RUN_SCRIPT_PATH = ROOT / "evals/codex/scripts/run_prompts.py"
REPORT_SCRIPT_PATH = ROOT / "evals/codex/scripts/render_report.py"
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
            "RFC 9457 Problem Details",
            "FilterSchema",
            "Query[",
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
        self.assertEqual(thresholds["minimum_average_lift_percent"], 15)
        self.assertEqual(thresholds["maximum_drf_violation_count"], 0)

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

        self.assertIn("copyable team standard", api_standard)
        self.assertIn("edge-case checklist", api_standard)
        self.assertIn("constraints, indexes, locking", db_orders)
        self.assertIn("pytest or migration checks", db_orders)
        self.assertIn("thin Ninja endpoint", review_view_logic)
        self.assertNotIn("For pytest/TDD", api_standard)
        self.assertNotIn("For pytest/TDD", db_orders)

        review_fat_model = module.dddjango_developer_instructions(
            ROOT,
            case_id="pilot-review-fat-model",
        )
        self.assertIn("severity-ranked findings", review_fat_model)
        self.assertIn("assertNumQueries", review_fat_model)

        api_order = module.dddjango_developer_instructions(
            ROOT,
            case_id="pilot-api-order-create",
        )
        implementation_coupon = module.dddjango_developer_instructions(
            ROOT,
            case_id="pilot-implementation-coupon",
        )

        for instructions in [api_order, implementation_coupon]:
            self.assertIn("Keep under 900 words", instructions)
            self.assertIn("no full domain model", instructions)
            self.assertIn("only critical code", instructions)

        self.assertIn("Keep under 700 words", implementation_coupon)
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
        self.assertIn("Keep under 750 words", api_instructions)
        self.assertLess(len(api_instructions), len(module.dddjango_developer_instructions(ROOT)))

        negative_trigger = {
            "category": "trigger",
            "trigger_type": "negative",
            "prompt": "Rust로 문자열 slugify 함수를 작성해줘.",
            "expectations": ["korean_first"],
            "scoring_focus": ["Rust 코드만 제공한다."],
        }
        self.assertEqual(
            module.dddjango_developer_instructions(
                ROOT,
                case_id="trigger-negative-rust-function",
                case=negative_trigger,
            ),
            "",
        )

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
        self.assertIn("Do not output DRF implementation code", conflict_instructions)
        self.assertIn("produce no DRF code", conflict_instructions)

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

        self.assertIn("맥락이 불명확합니다", ambiguous_instructions)
        self.assertIn("Django라면", ambiguous_instructions)

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
            self.assertFalse(
                any(part.startswith("developer_instructions=") for part in commands[0])
            )

    def test_render_report_creates_html_comparison_dashboard(self):
        module = load_module(REPORT_SCRIPT_PATH)

        with tempfile.TemporaryDirectory() as temp_dir:
            iteration = Path(temp_dir)
            (iteration / "baseline").mkdir()
            (iteration / "dddjango").mkdir()
            (iteration / "answer-key").mkdir()
            (iteration / "baseline/case-a.output.md").write_text(
                "# Baseline Output\n\n- **plain** `result`\n"
            )
            (iteration / "dddjango/case-a.output.md").write_text(
                "# dddjango Output\n\n```python\nprint('ok')\n```\n"
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
                            "variant": "dddjango",
                            "duration_sec": 12.0,
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
            self.assertIn("Usability Summary", html)
            self.assertIn("Realistic Layout", html)
            self.assertIn("Korean Quality", html)
            self.assertIn("바로 적용 가능", html)
            self.assertIn("Case Comparison: Without Skill vs With dddjango", html)
            self.assertIn("Completed Cases", html)
            self.assertIn("Case A title", html)
            self.assertIn("api-design", html)
            self.assertIn("korean_first, django_ninja_compliance", html)
            self.assertIn("Without Skill", html)
            self.assertIn("With dddjango", html)
            self.assertIn("+10.0", html)
            self.assertNotIn("file://", html)
            self.assertIn('href="artifacts/case-a-baseline.html"', html)
            self.assertIn('href="artifacts/case-a-dddjango.html"', html)
            self.assertIn('href="artifacts/case-a-answer-key.html"', html)

            baseline_artifact = iteration / "artifacts/case-a-baseline.html"
            dddjango_artifact = iteration / "artifacts/case-a-dddjango.html"
            answer_key_artifact = iteration / "artifacts/case-a-answer-key.html"
            self.assertTrue(baseline_artifact.exists())
            self.assertTrue(dddjango_artifact.exists())
            self.assertTrue(answer_key_artifact.exists())
            self.assertIn("<h1>Baseline Output</h1>", baseline_artifact.read_text())
            self.assertIn("<li><strong>plain</strong> <code>result</code></li>", baseline_artifact.read_text())
            self.assertIn("<h1>dddjango Output</h1>", dddjango_artifact.read_text())
            self.assertIn("<pre><code>", dddjango_artifact.read_text())
            self.assertIn("print(&#x27;ok&#x27;)", dddjango_artifact.read_text())
            self.assertIn("Case A title", answer_key_artifact.read_text())

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


if __name__ == "__main__":
    unittest.main()
