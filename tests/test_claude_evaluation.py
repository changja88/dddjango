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
CLAUDE_INIT_SCRIPT_PATH = ROOT / "evals/claude/scripts/init_iteration.py"
CLAUDE_RUN_SCRIPT_PATH = ROOT / "evals/claude/scripts/run_prompts.py"
REPORT_SCRIPT_PATH = ROOT / "evals/codex/scripts/render_report.py"


def load_module(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ClaudeEvaluationAssetTests(unittest.TestCase):
    def test_claude_init_iteration_reuses_pilot_cases(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "iteration-1"

            subprocess.run(
                [
                    sys.executable,
                    str(CLAUDE_INIT_SCRIPT_PATH),
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

            self.assertEqual(len(list((output_dir / "baseline").glob("*.prompt.md"))), 8)
            self.assertEqual(len(list((output_dir / "dddjango").glob("*.prompt.md"))), 8)
            self.assertEqual(len(json.loads((output_dir / "grades.json").read_text())), 16)
            self.assertIn(
                "# Claude dddjango Evaluation Iteration",
                (output_dir / "SUMMARY.md").read_text(),
            )

    def test_claude_baseline_command_disables_skills_and_plugins(self):
        module = load_module(CLAUDE_RUN_SCRIPT_PATH)

        with tempfile.TemporaryDirectory() as temp_dir:
            prompt_file = Path(temp_dir) / "baseline/pilot-negative-drf.prompt.md"
            prompt_file.parent.mkdir()
            prompt_file.write_text("## Prompt\n\nDRF ViewSet으로 상품 API 만들어줘.\n")

            command = module.build_claude_command(
                prompt_file=prompt_file,
                variant="baseline",
                model="sonnet",
                plugin_dir=ROOT,
            )

        self.assertIn("claude", command)
        self.assertIn("-p", command)
        self.assertIn("--disable-slash-commands", command)
        self.assertIn("--model", command)
        self.assertIn("sonnet", command)
        self.assertNotIn("--plugin-dir", command)
        self.assertNotIn("--append-system-prompt", command)
        self.assertEqual(command[-1], "DRF ViewSet으로 상품 API 만들어줘.")

    def test_claude_dddjango_command_loads_plugin_and_case_policy(self):
        module = load_module(CLAUDE_RUN_SCRIPT_PATH)

        with tempfile.TemporaryDirectory() as temp_dir:
            prompt_file = Path(temp_dir) / "dddjango/pilot-negative-drf.prompt.md"
            prompt_file.parent.mkdir()
            prompt_file.write_text("## Prompt\n\nDRF ViewSet으로 상품 API 만들어줘.\n")

            system_prompt = module.claude_dddjango_system_prompt("pilot-negative-drf")
            command = module.build_claude_command(
                prompt_file=prompt_file,
                variant="dddjango",
                model="",
                plugin_dir=ROOT,
                system_prompt=system_prompt,
            )

        self.assertIn("--plugin-dir", command)
        self.assertIn(str(ROOT), command)
        self.assertIn("--append-system-prompt", command)
        self.assertNotIn("--disable-slash-commands", command)
        self.assertIn("produce no DRF code", system_prompt)
        self.assertIn("convert to Django Ninja", system_prompt)

    def test_report_renderer_can_label_claude_report(self):
        module = load_module(REPORT_SCRIPT_PATH)

        with tempfile.TemporaryDirectory() as temp_dir:
            iteration = Path(temp_dir)
            (iteration / "baseline").mkdir()
            (iteration / "dddjango").mkdir()
            (iteration / "answer-key").mkdir()
            (iteration / "baseline/case-a.output.md").write_text("baseline output")
            (iteration / "dddjango/case-a.output.md").write_text("dddjango output")
            (iteration / "answer-key/case-a.json").write_text(
                json.dumps(
                    {
                        "title": "Case A title",
                        "category": "api-design",
                        "expectations": ["korean_first"],
                    },
                    ensure_ascii=False,
                )
            )
            scores = {
                "domain_fit": 10,
                "django_ninja_compliance": 20,
                "actionability": 10,
                "architecture_quality": 10,
                "testing_quality": 5,
                "korean_first": 10,
                "conciseness": 5,
                "safety": 5,
            }
            flags = {
                "korean_first": True,
                "django_ninja_used": True,
                "drf_endorsed": False,
                "negative_control_passed": False,
            }
            (iteration / "grades.json").write_text(
                json.dumps(
                    [
                        {"case_id": "case-a", "variant": "baseline", "scores": scores, "flags": flags},
                        {"case_id": "case-a", "variant": "dddjango", "scores": scores, "flags": flags},
                    ],
                    ensure_ascii=False,
                )
                + "\n"
            )
            (iteration / "timing.json").write_text(
                json.dumps(
                    [
                        {"case_id": "case-a", "variant": "baseline", "duration_sec": 10.0},
                        {"case_id": "case-a", "variant": "dddjango", "duration_sec": 11.0},
                    ]
                )
                + "\n"
            )

            report_path = module.render_report(iteration, platform="Claude")
            html = report_path.read_text()

            self.assertIn("dddjango Claude Evaluation Report", html)
            self.assertIn("Case Comparison: Without Skill vs With dddjango", html)


if __name__ == "__main__":
    unittest.main()
