#!/usr/bin/env python3
"""Unit tests for the P6 integration-flow eval runner."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "workspace/scripts/p6_integration_eval.py"
FIXTURE_ROOT = ROOT / "workspace/develop/eval/fixtures/integration-flows"

spec = importlib.util.spec_from_file_location("p6_integration_eval", SCRIPT)
assert spec is not None
p6_integration_eval = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["p6_integration_eval"] = p6_integration_eval
spec.loader.exec_module(p6_integration_eval)


class P6IntegrationEvalTests(unittest.TestCase):
    def paths(self, output_dir: Path) -> p6_integration_eval.base.Paths:
        return p6_integration_eval.base.Paths(
            fixture_root=FIXTURE_ROOT,
            output_dir=output_dir,
            repo_root=ROOT,
        )

    def test_fixture_bucket_scores_all_integration_flows_as_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            raw = p6_integration_eval.run_bucket(self.paths(Path(tmp)), "integration-flows", "unit-p6")

        self.assertEqual(raw["case_count"], 4)
        self.assertEqual(raw["result_count"], 8)
        self.assertEqual(raw["status"], "pass")
        self.assertEqual(raw["status_counts"], {"pass": 8, "partial": 0, "fail": 0, "not-scored": 0})
        self.assertFalse(raw["model_backed"])

    def test_source_runtime_leakage_is_guardrail_failure(self) -> None:
        case = p6_integration_eval.base.case_by_id(FIXTURE_ROOT, "p6-source-runtime-governance-boundary")
        answer = {
            "loaded_skill": "dddjango:source-reference-audit",
            "claims": ["source-runtime-boundary", "leakage-restraint", "handoff-contract-coverage", "forbidden-overclaim"],
            "overclaims": False,
            "answer_text": "Use workspace/reference/final.md as a runtime-facing allowed reference.",
        }

        result = p6_integration_eval.score_p6_answer(case=case, variant="with-plugin", answer=answer)

        self.assertEqual(result["status"], "fail")
        self.assertIn("source-leakage", result["failure_semantics"])
        self.assertEqual(result["checks"]["source_runtime_leakage"]["hit_count"], 1)

    def test_tiny_edit_rejects_workflow_overreach(self) -> None:
        case = p6_integration_eval.base.case_by_id(FIXTURE_ROOT, "p6-tiny-edit-opt-out-restraint")
        answer = {
            "loaded_skill": "dddjango:workflow-dddjango-subagents; dddjango:implementation-python",
            "claims": ["restraint-boundary-coverage", "no-workflow-overreach", "forbidden-overclaim"],
            "overclaims": False,
            "answer_text": "Use a role map for the typo fix.",
        }

        result = p6_integration_eval.score_p6_answer(case=case, variant="with-plugin", answer=answer)

        self.assertEqual(result["status"], "fail")
        self.assertIn("skill-responsibility-intrusion", result["failure_semantics"])

    def test_tiny_edit_accepts_empty_loaded_skill_when_none_is_allowed(self) -> None:
        case = p6_integration_eval.base.case_by_id(FIXTURE_ROOT, "p6-tiny-edit-opt-out-restraint")
        answer = {
            "loaded_skill": "",
            "claims": ["restraint-boundary-coverage", "no-workflow-overreach", "forbidden-overclaim"],
            "overclaims": False,
            "answer_text": "def calc_total(price): return price",
        }

        result = p6_integration_eval.score_p6_answer(case=case, variant="with-plugin", answer=answer)

        self.assertEqual(result["status"], "pass")
        self.assertNotIn("wrong-routing", result["failure_semantics"])
        self.assertTrue(result["checks"]["loaded_skill"]["ok"])

    def test_model_targeted_suite_records_two_model_backed_iterations(self) -> None:
        @dataclass
        class FakeCompletedProcess:
            returncode: int
            stdout: str
            stderr: str

        def fake_runner(command: list[str], *, cwd: Path, final_path: Path) -> FakeCompletedProcess:
            del command, cwd
            case_variant = final_path.parent.name
            variant = "with-plugin" if case_variant.endswith("-with-plugin") else "baseline"
            case_id = case_variant.removesuffix(f"-{variant}")
            case = p6_integration_eval.base.case_by_id(FIXTURE_ROOT, case_id)
            oracle = case["oracle"]
            final_path.parent.mkdir(parents=True, exist_ok=True)
            loaded_skill = "; ".join(p6_integration_eval.required_loaded_skills(oracle)) or oracle["loaded_skill"]
            final_path.write_text(
                json.dumps(
                    {
                        "loaded_skill": loaded_skill,
                        "claims": oracle["required_claims"],
                        "overclaims": False,
                        "answer_text": f"model answer for {case_id}",
                    }
                ),
                encoding="utf-8",
            )
            return FakeCompletedProcess(
                returncode=0,
                stdout='{"command":"/bin/zsh -lc \\"sed /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/workflow-dddjango-subagents/SKILL.md\\""}\n',
                stderr="trace cwd=/private/tmp/dddjango-p8-model/case",
            )

        with tempfile.TemporaryDirectory() as tmp:
            paths = self.paths(Path(tmp) / "run")
            summary = p6_integration_eval.run_targeted_suite(
                paths,
                bucket="integration-flows",
                run_id="unit-model-p6",
                iterations=2,
                model_backed=True,
                runtime_channel="external",
                work_root=Path(tmp) / "work",
                variants=("with-plugin",),
                runner=fake_runner,
            )
            raw = json.loads((paths.output_dir / "raw" / "targeted-run-1.json").read_text(encoding="utf-8"))
            stdout_text = (
                paths.output_dir
                / "raw/model-executions/p6-composite-order-ddd-db-api-django-test.with-plugin.stdout.jsonl"
            ).read_text(encoding="utf-8")
            stderr_text = (
                paths.output_dir
                / "raw/model-executions/p6-composite-order-ddd-db-api-django-test.with-plugin.stderr.txt"
            ).read_text(encoding="utf-8")

        self.assertEqual(summary["status"], "pass")
        self.assertTrue(summary["model_backed"])
        self.assertEqual(summary["variance_status"], "stable-pass")
        self.assertEqual(summary["variants"], ["with-plugin"])
        self.assertEqual(raw["status_counts"]["not-scored"], 0)
        self.assertEqual(raw["result_count"], 4)
        self.assertNotIn("/Users/hyun", stdout_text + stderr_text)
        self.assertNotIn("/private/tmp", stdout_text + stderr_text)
        self.assertIn("<installed-cache-root>", stdout_text)
        self.assertIn("<tmp>", stderr_text)

    def test_validate_run_accepts_model_bucket_with_stable_targeted_suite_proof(self) -> None:
        @dataclass
        class FakeCompletedProcess:
            returncode: int
            stdout: str
            stderr: str

        def fake_runner(command: list[str], *, cwd: Path, final_path: Path) -> FakeCompletedProcess:
            del command, cwd
            case_variant = final_path.parent.name
            variant = "with-plugin" if case_variant.endswith("-with-plugin") else "baseline"
            case_id = case_variant.removesuffix(f"-{variant}")
            case = p6_integration_eval.base.case_by_id(FIXTURE_ROOT, case_id)
            oracle = case["oracle"]
            final_path.parent.mkdir(parents=True, exist_ok=True)
            loaded_skill = "; ".join(p6_integration_eval.required_loaded_skills(oracle)) or oracle["loaded_skill"]
            final_path.write_text(
                json.dumps(
                    {
                        "loaded_skill": loaded_skill,
                        "claims": oracle["required_claims"],
                        "overclaims": False,
                        "answer_text": f"model answer for {case_id}",
                    }
                ),
                encoding="utf-8",
            )
            return FakeCompletedProcess(returncode=0, stdout='{"event":"done"}\n', stderr="")

        with tempfile.TemporaryDirectory() as tmp:
            paths = self.paths(Path(tmp) / "run")
            raw = p6_integration_eval.run_bucket(
                paths,
                "integration-flows",
                "unit-model-p6",
                model_backed=True,
                runtime_channel="external",
                work_root=Path(tmp) / "work",
                variants=("with-plugin",),
                runner=fake_runner,
            )
            p6_integration_eval.base.write_json(
                paths.output_dir / "raw" / "targeted-suite.json",
                {
                    "schema_version": "p6-integration-model-targeted-suite/v1",
                    "run_id": "unit-model-p6-targeted",
                    "bucket": "integration-flows",
                    "iterations": 2,
                    "variants": raw["variants"],
                    "status": "pass",
                    "model_backed": True,
                    "runtime_channel": "external",
                    "variance_status": "stable-pass",
                    "runs": [],
                },
            )
            p6_integration_eval.render_report(paths.output_dir)
            validation = p6_integration_eval.validate_run(paths.output_dir, ROOT)

        self.assertEqual(validation["status"], "pass")
        self.assertEqual(validation["failures"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
