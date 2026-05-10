#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).with_name("run_eval_bucket.py")


def load_runner():
    spec = importlib.util.spec_from_file_location("run_eval_bucket", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class RunEvalBucketTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = load_runner()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "repo"
        self.root.mkdir()
        self.workspace_root = Path(self.tmp.name) / "workspaces"
        self.runner.common.REPO_ROOT = self.root
        self.runner.common.EVAL_ROOT = self.root / "workspace/develop/eval"
        self.runner.REPO_ROOT = self.root
        self.runner.EVAL_ROOT = self.runner.common.EVAL_ROOT
        self.runner.CODE_CAPTURE_METADATA = (
            self.runner.common.EVAL_ROOT / "code/cases/plugin/code-capture.json"
        )
        (self.root / "README.md").write_text("subject repo\n", encoding="utf-8")

    def write_case(
        self,
        bucket: str = "response",
        case_id: str = "case-response-one",
        public_text: str = "사용자 요청입니다.\n",
    ) -> None:
        case_path = (
            self.runner.common.EVAL_ROOT
            / bucket
            / "cases/plugin/public"
            / f"{case_id}.md"
        )
        answer_path = self.runner.common.EVAL_ROOT / bucket / "answer" / f"{case_id}.yaml"
        case_path.parent.mkdir(parents=True, exist_ok=True)
        answer_path.parent.mkdir(parents=True, exist_ok=True)
        case_path.write_text(public_text, encoding="utf-8")
        answer_path.write_text(
            f"id: {case_id}\ncase_id: {case_id}\nbucket: {bucket}\nkind: {bucket}\n",
            encoding="utf-8",
        )

    def write_code_capture_metadata(
        self,
        *,
        case_id: str = "case-code-one",
        capture_code: bool = True,
        subject_repo: str = "workspace/develop/eval/code/fixtures/shop_service",
    ) -> None:
        metadata_path = self.runner.CODE_CAPTURE_METADATA
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        metadata_path.write_text(
            json.dumps(
                {
                    "cases": {
                        case_id: {
                            "captureCode": capture_code,
                            "subjectRepo": subject_repo,
                        }
                    }
                }
            )
            + "\n",
            encoding="utf-8",
        )
        subject_path = self.root / subject_repo
        subject_path.mkdir(parents=True, exist_ok=True)
        (subject_path / "pyproject.toml").write_text("[project]\nname = 'fixture'\n", encoding="utf-8")

    def fake_run_command(self, command, *, prompt, cwd, timeout_seconds):
        self.commands.append((command, prompt, cwd, timeout_seconds))
        if command[:3] == ["codex", "debug", "prompt-input"]:
            return subprocess.CompletedProcess(command, 0, '{"messages": []}\n', "")
        if "exec" in command:
            return subprocess.CompletedProcess(command, 7, "event stream\n", "stderr text\n")
        return subprocess.CompletedProcess(command, 0, "", "")

    def test_skip_exec_writes_required_raw_artifacts_for_both_variants(self) -> None:
        self.write_case()

        result = self.runner.main(
            [
                "--bucket",
                "response",
                "--run-id",
                "run-one",
                "--workspace-root",
                str(self.workspace_root),
                "--skip-exec",
            ]
        )

        self.assertEqual(result, 0)
        raw = self.runner.common.EVAL_ROOT / "response/runs/run-one/raw"
        with_variant = self.runner.common.VARIANTS[1]
        for name in (
            "case-response-one-public-prompt.md",
            "case-response-one-operator-prompt.txt",
            "case-response-one-baseline.txt",
            f"case-response-one-{with_variant}.txt",
            "case-response-one-baseline-isolation.json",
            "case-response-one-baseline-events.jsonl",
            f"case-response-one-{with_variant}-events.jsonl",
            "case-response-one-baseline.stderr.txt",
            f"case-response-one-{with_variant}.stderr.txt",
            "case-response-one-baseline-command.txt",
            f"case-response-one-{with_variant}-command.txt",
            "case-response-one-baseline-exit.txt",
            f"case-response-one-{with_variant}-exit.txt",
        ):
            self.assertTrue((raw / name).is_file(), name)
        self.assertFalse((raw / "case-response-one-baseline-prompt-input.json").exists())
        isolation = json.loads((raw / "case-response-one-baseline-isolation.json").read_text(encoding="utf-8"))
        self.assertTrue(isolation["commandUsesIgnoreUserConfig"])
        self.assertTrue(isolation["forbiddenPathsAbsent"])

    def test_exec_mode_writes_command_exit_stdout_and_stderr_artifacts(self) -> None:
        self.write_case()
        self.commands = []

        with patch.object(self.runner, "run_command", side_effect=self.fake_run_command):
            result = self.runner.main(
                [
                    "--bucket",
                    "response",
                    "--run-id",
                    "run-two",
                    "--case",
                    "case-response-one",
                    "--workspace-root",
                    str(self.workspace_root),
                ]
            )

        self.assertEqual(result, 0)
        raw = self.runner.common.EVAL_ROOT / "response/runs/run-two/raw"
        with_variant = self.runner.common.VARIANTS[1]
        self.assertEqual((raw / "case-response-one-baseline-exit.txt").read_text(encoding="utf-8"), "7\n")
        self.assertEqual((raw / f"case-response-one-{with_variant}-exit.txt").read_text(encoding="utf-8"), "7\n")
        self.assertEqual(
            (raw / "case-response-one-baseline-events.jsonl").read_text(encoding="utf-8"),
            "event stream\n",
        )
        self.assertEqual(
            (raw / f"case-response-one-{with_variant}.stderr.txt").read_text(encoding="utf-8"),
            "stderr text\n",
        )
        baseline_command = (raw / "case-response-one-baseline-command.txt").read_text(encoding="utf-8")
        with_ddjango_command = (raw / f"case-response-one-{with_variant}-command.txt").read_text(encoding="utf-8")
        self.assertIn("--ignore-user-config", baseline_command)
        self.assertIn("--ignore-rules", baseline_command)
        self.assertNotIn("--ignore-user-config", with_ddjango_command)
        self.assertNotIn("--ignore-rules", with_ddjango_command)
        self.assertTrue((raw / f"case-response-one-{with_variant}-prompt-input.json").is_file())
        self.assertFalse((raw / "case-response-one-baseline-prompt-input.json").exists())

    def test_code_bucket_rejects_case_without_capture_code_enabled(self) -> None:
        self.write_case(bucket="code", case_id="case-code-one")
        self.write_code_capture_metadata(capture_code=False)

        with self.assertRaisesRegex(SystemExit, "captureCode: true"):
            self.runner.main(
                [
                    "--bucket",
                    "code",
                    "--run-id",
                    "run-code",
                    "--case",
                    "case-code-one",
                    "--workspace-root",
                    str(self.workspace_root),
                    "--skip-exec",
                ]
            )

    def test_code_bucket_skip_exec_captures_code_artifacts_for_marked_case(self) -> None:
        self.write_case(bucket="code", case_id="case-code-one")
        self.write_code_capture_metadata()

        result = self.runner.main(
            [
                "--bucket",
                "code",
                "--run-id",
                "run-code",
                "--case",
                "case-code-one",
                "--variant",
                "baseline",
                "--workspace-root",
                str(self.workspace_root),
                "--skip-exec",
            ]
        )

        self.assertEqual(result, 0)
        run_dir = self.runner.common.EVAL_ROOT / "code/runs/run-code"
        self.assertTrue((run_dir / "code/case-code-one/baseline/changed-files.json").is_file())
        self.assertTrue((run_dir / "code/case-code-one/baseline/diff.patch").is_file())
        command = (run_dir / "raw/case-code-one-baseline-command.txt").read_text(encoding="utf-8")
        self.assertIn("-s workspace-write", command)


if __name__ == "__main__":
    unittest.main()
