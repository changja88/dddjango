#!/usr/bin/env python3
"""Unit tests for the fixture-only P4 eval skeleton."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "workspace/scripts/eval_skeleton.py"
FIXTURE_ROOT = ROOT / "workspace/develop/eval/fixtures/mini-bucket"

spec = importlib.util.spec_from_file_location("eval_skeleton", SCRIPT)
assert spec is not None
eval_skeleton = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["eval_skeleton"] = eval_skeleton
spec.loader.exec_module(eval_skeleton)


class EvalSkeletonTests(unittest.TestCase):
    def test_run_bucket_distinguishes_fixture_statuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = eval_skeleton.Paths(fixture_root=FIXTURE_ROOT, output_dir=Path(tmp))
            raw = eval_skeleton.run_bucket(paths, "mini-bucket", "unit-mini-bucket")

        self.assertEqual(raw["status_counts"], {"pass": 6, "partial": 2, "fail": 12, "not-scored": 4})
        self.assertEqual(raw["hard_failure_count"], 18)
        self.assertEqual(raw["fixture_mismatch_count"], 0)

    def test_missing_and_malformed_oracles_are_not_scored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = eval_skeleton.Paths(fixture_root=FIXTURE_ROOT, output_dir=Path(tmp))
            missing = eval_skeleton.run_one(paths, "p4-missing-oracle", "with-plugin")
            malformed = eval_skeleton.run_one(paths, "p4-malformed-oracle", "baseline")

        self.assertEqual(missing["status"], "not-scored")
        self.assertIn("missing-oracle", missing["failure_semantics"])
        self.assertEqual(malformed["status"], "not-scored")
        self.assertIn("malformed-oracle", malformed["failure_semantics"])

    def test_pre_redaction_leak_fails_even_when_persisted_text_is_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = eval_skeleton.Paths(fixture_root=FIXTURE_ROOT, output_dir=Path(tmp))
            result = eval_skeleton.run_one(paths, "p4-sanitizer-only-leak", "baseline")

        self.assertEqual(result["status"], "fail")
        self.assertIn("raw-leakage", result["failure_semantics"])
        self.assertNotIn("persisted-leakage", result["failure_semantics"])

    def test_command_claim_requires_structured_event(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = eval_skeleton.Paths(fixture_root=FIXTURE_ROOT, output_dir=Path(tmp))
            result = eval_skeleton.run_one(paths, "p4-prompt-only-command-claim", "baseline")

        self.assertEqual(result["status"], "fail")
        self.assertIn("missing-structured-command-evidence", result["failure_semantics"])
        self.assertFalse(result["checks"]["required_command"]["observed_in_structured_event"])

    def test_korean_negation_is_not_routing_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = eval_skeleton.Paths(fixture_root=FIXTURE_ROOT, output_dir=Path(tmp))
            result = eval_skeleton.run_one(paths, "p4-korean-negation-false-positive", "baseline")

        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["checks"]["loaded_skill"]["actual"], "dddjango:architecture-api")

    def test_validate_run_compares_raw_and_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = eval_skeleton.Paths(fixture_root=FIXTURE_ROOT, output_dir=Path(tmp))
            eval_skeleton.run_bucket(paths, "mini-bucket", "unit-mini-bucket")
            eval_skeleton.render_report(paths.output_dir)
            validation = eval_skeleton.validate_run(paths.output_dir)

        self.assertEqual(validation["status"], "fail")
        self.assertIn("not-scored-present", {failure["kind"] for failure in validation["failures"]})
        self.assertNotIn("report-raw-result-mismatch", {failure["kind"] for failure in validation["failures"]})

    def test_stale_report_detection_uses_raw_digest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = eval_skeleton.Paths(fixture_root=FIXTURE_ROOT, output_dir=Path(tmp))
            eval_skeleton.run_bucket(paths, "mini-bucket", "unit-mini-bucket")
            eval_skeleton.render_report(paths.output_dir)
            report_path = paths.output_dir / "report/report.json"
            report = json.loads(report_path.read_text(encoding="utf-8"))
            report["source_raw_digest"] = "stale"
            report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            validation = eval_skeleton.validate_run(paths.output_dir)

        self.assertIn("stale-report", {failure["kind"] for failure in validation["failures"]})


if __name__ == "__main__":
    unittest.main(verbosity=2)
