#!/usr/bin/env python3
"""Unit tests for the P5 individual-skill fixture scorer."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
