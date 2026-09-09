"""실패를 숨기거나 사례를 섞어 속도 효과를 과장하지 않는 집계 검사."""

import unittest
import json
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

from summarize import group_trials
import summarize as summary_module
from experiment import digest


class SummaryTests(unittest.TestCase):
    def test_different_cases_are_separate_and_errors_are_counted(self):
        rows = [
            {"case": "A", "arm": "full", "wall_ms": 1000, "error": None, "grade": {"all_pass": True}},
            {"case": "A", "arm": "full", "wall_ms": 3000, "error": None, "grade": {"all_pass": False}},
            {"case": "A", "arm": "full", "wall_ms": 10, "error": "limit", "grade": None},
            {"case": "B", "arm": "full", "wall_ms": 5000, "error": None, "grade": {"all_pass": True}},
        ]
        groups = group_trials(rows)
        self.assertIn("A/full", groups)
        self.assertIn("B/full", groups)
        self.assertEqual(groups["A/full"]["attempts"], 3)
        self.assertEqual(groups["A/full"]["all_pass"], 1)
        self.assertEqual(groups["A/full"]["errors"], 1)
        self.assertFalse(groups["A/full"]["all_trials_valid"])
        self.assertEqual(groups["A/full"]["wall_ms_all_attempts"]["median"], 1000)
        self.assertEqual(groups["A/full"].get("valid_model_trials"), 2)
        self.assertEqual(groups["A/full"]["wall_ms_valid_model_trials"]["median"], 2000)
        self.assertEqual(groups["B/full"]["wall_ms_all_attempts"]["median"], 5000)

    def test_empty_trials_are_not_successful(self):
        self.assertEqual(group_trials([]), {})

    def test_retry_is_counted_once_and_original_denial_remains_visible(self):
        source = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory)
            for name in ["cases.json", "manifest.json", "offline-results.json", "engine-results.json"]:
                shutil.copyfile(source / name, fixture / name)
            for name in ["frozen", "trials"]:
                shutil.copytree(source / name, fixture / name)
            blocked_text = (fixture / "trials/3-guard-linked.json").read_text()
            blocked = json.loads(blocked_text)
            retry = json.loads((fixture / "trials/1-guard-linked.json").read_text())
            retry.update({"trial": "3-guard-linked", "repeat": 3, "retry_of": "3-guard-linked",
                          "execution_batch": "user-switched-account", "original_record_sha256": digest(blocked_text)})
            retry_dir = fixture / "retries/round-1"
            retry_dir.mkdir(parents=True)
            (retry_dir / "3-guard-linked.json").write_text(json.dumps(retry))
            with patch.object(summary_module, "ROOT", fixture):
                result = summary_module.summarize(True)
            self.assertEqual(result["valid_model_trials"], 13)
            self.assertEqual(result["recorded_attempts"], 19)
            self.assertEqual(result["original_groups"]["guard/linked"]["errors"], 1)
            self.assertEqual(result["groups"]["guard/linked"]["valid_model_trials"], 3)
            self.assertEqual(result["resumed_groups"]["guard/linked"]["valid_model_trials"], 1)
            self.assertEqual((fixture / "trials/3-guard-linked.json").read_text(), blocked_text)


if __name__ == "__main__":
    unittest.main()
