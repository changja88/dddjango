import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "evals/codex/cases/pilot.jsonl"
SCHEMA_PATH = ROOT / "evals/codex/rubrics/grading-schema.json"
GRADE_SCRIPT_PATH = ROOT / "evals/codex/scripts/grade_outputs.py"
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
            "rest_framework",
            "ViewSet",
            "Serializer",
        ]:
            with self.subTest(required=required):
                self.assertIn(required, body)

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

    def test_grade_outputs_summarizes_baseline_and_dddjango_scores(self):
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
            },
            {
                "case_id": "case-1",
                "variant": "dddjango",
                "scores": {"domain_fit": 18, "korean_first": 10},
            },
        ]

        summary = module.summarize_grades(grades, schema)

        self.assertEqual(summary["variants"]["baseline"]["average_score"], 15.0)
        self.assertEqual(summary["variants"]["dddjango"]["average_score"], 28.0)
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
            self.assertIn(first_grade["variant"], {"baseline", "dddjango"})

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

    def test_render_report_creates_html_comparison_dashboard(self):
        module = load_module(REPORT_SCRIPT_PATH)

        with tempfile.TemporaryDirectory() as temp_dir:
            iteration = Path(temp_dir)
            (iteration / "baseline").mkdir()
            (iteration / "dddjango").mkdir()
            (iteration / "answer-key").mkdir()
            (iteration / "baseline/case-a.output.md").write_text("baseline output")
            (iteration / "dddjango/case-a.output.md").write_text("dddjango output")
            (iteration / "answer-key/case-a.json").write_text("{}")
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
            self.assertIn("+10.0", html)
            self.assertIn("baseline/case-a.output.md", html)
            self.assertIn("dddjango/case-a.output.md", html)
            self.assertIn("answer-key/case-a.json", html)


if __name__ == "__main__":
    unittest.main()
