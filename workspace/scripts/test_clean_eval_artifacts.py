#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("clean_eval_artifacts.py")


def load_cleaner():
    spec = importlib.util.spec_from_file_location("clean_eval_artifacts", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CleanEvalArtifactsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cleaner = load_cleaner()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "repo"
        self.eval_root = self.root / "workspace/develop/eval"
        self.lv_root = self.root / "workspace/plan/skill_lv_up_plan"
        self.cleaner.REPO_ROOT = self.root
        self.cleaner.EVAL_ROOT = self.eval_root

    def write_tree(self) -> None:
        for bucket in self.cleaner.BUCKETS:
            (self.eval_root / bucket / "runs/run-one/raw").mkdir(parents=True)
            (self.eval_root / bucket / "latest").mkdir(parents=True)
            (self.eval_root / bucket / "latest/summary.md").write_text("latest\n", encoding="utf-8")
            (self.eval_root / bucket / "latest-valid").mkdir(parents=True)
            (self.eval_root / bucket / "latest-valid/report.html").write_text(
                "report\n",
                encoding="utf-8",
            )
            (self.eval_root / bucket / "eval_goal.md").write_text("goal\n", encoding="utf-8")
            (self.eval_root / bucket / "cases/plugin/public").mkdir(parents=True)
            (self.eval_root / bucket / "answer").mkdir(parents=True)
            for section in ("analysis", "plan"):
                path = self.lv_root / bucket / section / "20260517-120000-try01-topic.md"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("iteration\n", encoding="utf-8")

    def test_collect_delete_targets_only_generated_artifacts(self) -> None:
        self.write_tree()

        targets = self.cleaner.collect_delete_targets()
        target_text = sorted(path.relative_to(self.root).as_posix() for path in targets)

        self.assertIn("workspace/develop/eval/runtime/runs/run-one", target_text)
        self.assertIn("workspace/develop/eval/runtime/latest/summary.md", target_text)
        self.assertIn("workspace/develop/eval/runtime/latest-valid/report.html", target_text)
        self.assertNotIn(
            "workspace/plan/skill_lv_up_plan/runtime/analysis/20260517-120000-try01-topic.md",
            target_text,
        )
        self.assertNotIn(
            "workspace/plan/skill_lv_up_plan/runtime/plan/20260517-120000-try01-topic.md",
            target_text,
        )
        self.assertNotIn("workspace/develop/eval/runtime/eval_goal.md", target_text)

    def test_dry_run_does_not_delete(self) -> None:
        self.write_tree()

        result = self.cleaner.main([])

        self.assertEqual(result, 0)
        self.assertTrue((self.eval_root / "runtime/runs/run-one").exists())
        self.assertTrue((self.eval_root / "runtime/latest-valid/report.html").exists())
        self.assertTrue((self.lv_root / "runtime/analysis/20260517-120000-try01-topic.md").exists())

    def test_confirmed_delete_removes_targets_and_preserves_sources(self) -> None:
        self.write_tree()

        result = self.cleaner.main(["--confirm-delete-generated-eval-artifacts"])

        self.assertEqual(result, 0)
        self.assertFalse((self.eval_root / "runtime/runs/run-one").exists())
        self.assertFalse((self.eval_root / "runtime/latest/summary.md").exists())
        self.assertFalse((self.eval_root / "runtime/latest-valid/report.html").exists())
        self.assertTrue((self.lv_root / "runtime/analysis/20260517-120000-try01-topic.md").is_file())
        self.assertTrue((self.lv_root / "runtime/plan/20260517-120000-try01-topic.md").is_file())
        self.assertTrue((self.eval_root / "runtime/eval_goal.md").is_file())


if __name__ == "__main__":
    unittest.main()
