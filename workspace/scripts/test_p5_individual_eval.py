#!/usr/bin/env python3
"""Unit tests for the P5 individual-skill fixture scorer."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "workspace/scripts/p5_individual_eval.py"
FIXTURE_ROOT = ROOT / "workspace/develop/eval/fixtures/individual-skills"

spec = importlib.util.spec_from_file_location("p5_individual_eval", SCRIPT)
assert spec is not None
p5_individual_eval = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["p5_individual_eval"] = p5_individual_eval
spec.loader.exec_module(p5_individual_eval)


class P5IndividualEvalTests(unittest.TestCase):
    def paths(self, output_dir: Path) -> p5_individual_eval.Paths:
        return p5_individual_eval.Paths(
            fixture_root=FIXTURE_ROOT,
            output_dir=output_dir,
            repo_root=ROOT,
        )

    def test_bucket_scores_all_individual_skill_results_as_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            raw = p5_individual_eval.run_bucket(self.paths(Path(tmp)), "individual-skills", "unit-p5")

        self.assertEqual(raw["case_count"], 26)
        self.assertEqual(raw["result_count"], 52)
        self.assertEqual(raw["status"], "pass")
        self.assertEqual(raw["status_counts"], {"pass": 52, "partial": 0, "fail": 0, "not-scored": 0})
        self.assertFalse(raw["model_backed"])

    def test_targeted_negative_surface_uses_expected_alternate_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = p5_individual_eval.run_one(
                self.paths(Path(tmp)),
                "p5-architecture-api-negative",
                "with-plugin",
                "unit-targeted",
            )

        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["expected_loaded_skill"], "dddjango:implementation-django-ninja")
        self.assertEqual(result["actual_loaded_skill"], "dddjango:implementation-django-ninja")

    def test_targeted_suite_records_two_clean_iterations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            summary = p5_individual_eval.run_targeted_suite(
                self.paths(Path(tmp)),
                "individual-skills",
                "unit-p5",
                2,
            )

        self.assertEqual(summary["status"], "pass")
        self.assertEqual(summary["iterations"], 2)
        self.assertEqual([run["status"] for run in summary["runs"]], ["pass", "pass"])

    def test_validate_run_requires_clean_scored_current_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.paths(Path(tmp))
            p5_individual_eval.run_bucket(paths, "individual-skills", "unit-p5")
            p5_individual_eval.render_report(paths.output_dir)
            validation = p5_individual_eval.validate_run(paths.output_dir, ROOT)

        self.assertEqual(validation["status"], "pass")
        self.assertEqual(validation["status_counts"]["not-scored"], 0)
        self.assertEqual(validation["failures"], [])

    def test_validate_run_detects_metadata_digest_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.paths(Path(tmp))
            p5_individual_eval.run_bucket(paths, "individual-skills", "unit-p5")
            p5_individual_eval.render_report(paths.output_dir)
            raw_path = paths.output_dir / "raw/run.json"
            raw = json.loads(raw_path.read_text(encoding="utf-8"))
            first_key = next(iter(raw["metadata_digests"]))
            raw["metadata_digests"][first_key] = "stale"
            raw["raw_digest"] = p5_individual_eval.digest_for_data(
                {key: value for key, value in raw.items() if key != "raw_digest"}
            )
            raw_path.write_text(json.dumps(raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            p5_individual_eval.render_report(paths.output_dir)
            validation = p5_individual_eval.validate_run(paths.output_dir, ROOT)

        self.assertEqual(validation["status"], "fail")
        self.assertIn("metadata-digest-mismatch", {failure["kind"] for failure in validation["failures"]})

    def test_model_answer_json_scores_against_existing_oracle(self) -> None:
        case = p5_individual_eval.case_by_id(FIXTURE_ROOT, "p5-architecture-api-positive")
        answer = p5_individual_eval.parse_model_answer(
            json.dumps(
                {
                    "loaded_skill": "dddjango:architecture-api",
                    "claims": [
                        "reference-criterion-coverage",
                        "required-observations",
                        "forbidden-overclaim",
                    ],
                    "overclaims": False,
                    "answer_text": "API contract answer",
                }
            )
        )

        result = p5_individual_eval.score_model_answer(case=case, variant="with-plugin", answer=answer)

        self.assertEqual(result["status"], "pass")
        self.assertTrue(result["model_backed"])
        self.assertEqual(result["actual_loaded_skill"], "dddjango:architecture-api")

    def test_model_answer_accepts_process_skill_plus_expected_loaded_skill(self) -> None:
        case = p5_individual_eval.case_by_id(FIXTURE_ROOT, "p5-architecture-api-positive")
        answer = p5_individual_eval.parse_model_answer(
            json.dumps(
                {
                    "loaded_skill": "using-superpowers + dddjango:architecture-api with REST contract boundary",
                    "claims": [
                        "reference-criterion-coverage",
                        "required-observations",
                        "forbidden-overclaim",
                    ],
                    "overclaims": False,
                    "answer_text": "API contract answer",
                }
            )
        )

        result = p5_individual_eval.score_model_answer(case=case, variant="with-plugin", answer=answer)

        self.assertEqual(result["status"], "pass")
        self.assertEqual(
            result["checks"]["loaded_skill"]["actual"],
            "using-superpowers + dddjango:architecture-api with REST contract boundary",
        )

    def test_model_answer_accepts_oracle_acceptable_loaded_skills(self) -> None:
        case = p5_individual_eval.case_by_id(FIXTURE_ROOT, "p5-source-reference-audit-negative")
        answer = p5_individual_eval.parse_model_answer(
            json.dumps(
                {
                    "loaded_skill": "superpowers:using-superpowers; dddjango:workflow-dddjango-subagents",
                    "claims": [
                        "reference-criterion-coverage",
                        "required-observations",
                        "forbidden-overclaim",
                    ],
                    "overclaims": False,
                    "answer_text": "Application behavior work is outside source-reference audit ownership.",
                }
            )
        )

        result = p5_individual_eval.score_model_answer(case=case, variant="with-plugin", answer=answer)

        self.assertEqual(result["status"], "pass")
        self.assertEqual(
            result["checks"]["loaded_skill"]["accepted"],
            ["dddjango:architecture-api", "dddjango:workflow-dddjango-subagents"],
        )

    def test_model_answer_schema_uses_supported_response_schema_keywords(self) -> None:
        claims_schema = p5_individual_eval.MODEL_ANSWER_SCHEMA["properties"]["claims"]

        self.assertNotIn("uniqueItems", claims_schema)

    def test_model_run_one_uses_installed_runtime_command_for_with_plugin(self) -> None:
        @dataclass
        class FakeCompletedProcess:
            returncode: int
            stdout: str
            stderr: str

        captured: dict[str, object] = {}

        def fake_runner(command: list[str], *, cwd: Path, final_path: Path) -> FakeCompletedProcess:
            captured["command"] = command
            captured["cwd"] = cwd
            captured["final_path"] = final_path
            final_path.parent.mkdir(parents=True, exist_ok=True)
            final_path.write_text(
                json.dumps(
                    {
                        "loaded_skill": "dddjango:architecture-api",
                        "claims": [
                            "reference-criterion-coverage",
                            "required-observations",
                            "forbidden-overclaim",
                        ],
                        "overclaims": False,
                        "answer_text": "API contract answer",
                    }
                ),
                encoding="utf-8",
            )
            return FakeCompletedProcess(returncode=0, stdout='{"event":"done"}\n', stderr="")

        with tempfile.TemporaryDirectory() as tmp:
            paths = self.paths(Path(tmp) / "run")
            result = p5_individual_eval.model_run_one(
                paths,
                case_id="p5-architecture-api-positive",
                variant="with-plugin",
                run_id="unit-model",
                runtime_channel="external",
                work_root=Path(tmp) / "work",
                runner=fake_runner,
            )

        self.assertEqual(result["status"], "pass")
        self.assertTrue(result["model_backed"])
        self.assertEqual(result["run_mode"], "model-backed-installed-runtime")
        command = captured["command"]
        self.assertIsInstance(command, list)
        self.assertIn("codex", command)
        self.assertNotIn("--ignore-user-config", command)
        self.assertIn("--output-schema", command)
        self.assertEqual(result["execution"]["returncode"], 0)

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
            case = p5_individual_eval.case_by_id(FIXTURE_ROOT, case_id)
            oracle = case["oracle"]
            final_path.parent.mkdir(parents=True, exist_ok=True)
            final_path.write_text(
                json.dumps(
                    {
                        "loaded_skill": oracle["loaded_skill"],
                        "claims": oracle["required_claims"],
                        "overclaims": False,
                        "answer_text": f"model answer for {case_id} {variant}",
                    }
                ),
                encoding="utf-8",
            )
            return FakeCompletedProcess(returncode=0, stdout='{"event":"done"}\n', stderr="")

        with tempfile.TemporaryDirectory() as tmp:
            paths = self.paths(Path(tmp) / "run")
            summary = p5_individual_eval.model_run_targeted_suite(
                paths,
                bucket="individual-skills",
                run_id="unit-model-targeted",
                iterations=2,
                runtime_channel="external",
                work_root=Path(tmp) / "work",
                variants=("with-plugin",),
                runner=fake_runner,
            )
            raw = json.loads((paths.output_dir / "raw" / "targeted-run-1.json").read_text(encoding="utf-8"))

        self.assertEqual(summary["status"], "pass")
        self.assertTrue(summary["model_backed"])
        self.assertEqual(summary["iterations"], 2)
        self.assertEqual([run["status"] for run in summary["runs"]], ["pass", "pass"])
        self.assertEqual([run["status_counts"]["not-scored"] for run in summary["runs"]], [0, 0])
        self.assertEqual(summary["variance_status"], "stable-pass")
        self.assertEqual(summary["variants"], ["with-plugin"])
        self.assertEqual(raw["variants"], ["with-plugin"])
        self.assertEqual(raw["result_count"], 26)

    def test_validate_run_rejects_single_pass_model_backed_raw_as_completion_evidence(self) -> None:
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
            case = p5_individual_eval.case_by_id(FIXTURE_ROOT, case_id)
            oracle = case["oracle"]
            final_path.parent.mkdir(parents=True, exist_ok=True)
            final_path.write_text(
                json.dumps(
                    {
                        "loaded_skill": oracle["loaded_skill"],
                        "claims": oracle["required_claims"],
                        "overclaims": False,
                        "answer_text": f"model answer for {case_id} {variant}",
                    }
                ),
                encoding="utf-8",
            )
            return FakeCompletedProcess(returncode=0, stdout='{"event":"done"}\n', stderr="")

        with tempfile.TemporaryDirectory() as tmp:
            paths = self.paths(Path(tmp) / "run")
            p5_individual_eval.model_run_bucket(
                paths,
                bucket="individual-skills",
                run_id="unit-model-single",
                runtime_channel="external",
                work_root=Path(tmp) / "work",
                runner=fake_runner,
            )
            p5_individual_eval.render_report(paths.output_dir)
            validation = p5_individual_eval.validate_run(paths.output_dir, ROOT)

        self.assertEqual(validation["status"], "fail")
        self.assertIn("model-backed-single-pass-provisional", {failure["kind"] for failure in validation["failures"]})

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
            case = p5_individual_eval.case_by_id(FIXTURE_ROOT, case_id)
            oracle = case["oracle"]
            final_path.parent.mkdir(parents=True, exist_ok=True)
            final_path.write_text(
                json.dumps(
                    {
                        "loaded_skill": oracle["loaded_skill"],
                        "claims": oracle["required_claims"],
                        "overclaims": False,
                        "answer_text": f"model answer for {case_id} {variant}",
                    }
                ),
                encoding="utf-8",
            )
            return FakeCompletedProcess(returncode=0, stdout='{"event":"done"}\n', stderr="")

        with tempfile.TemporaryDirectory() as tmp:
            paths = self.paths(Path(tmp) / "run")
            raw = p5_individual_eval.model_run_bucket(
                paths,
                bucket="individual-skills",
                run_id="unit-model-single",
                runtime_channel="external",
                work_root=Path(tmp) / "work",
                variants=("with-plugin",),
                runner=fake_runner,
            )
            p5_individual_eval.write_json(
                paths.output_dir / "raw" / "targeted-suite.json",
                {
                    "schema_version": "p5-individual-model-targeted-suite/v1",
                    "run_id": "unit-model-targeted",
                    "bucket": "individual-skills",
                    "iterations": 2,
                    "variants": raw["variants"],
                    "status": "pass",
                    "model_backed": True,
                    "runtime_channel": "external",
                    "variance_status": "stable-pass",
                    "runs": [],
                },
            )
            p5_individual_eval.render_report(paths.output_dir)
            validation = p5_individual_eval.validate_run(paths.output_dir, ROOT)

        self.assertEqual(validation["status"], "pass")
        self.assertEqual(validation["failures"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
