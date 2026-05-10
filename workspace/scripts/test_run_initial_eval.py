#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).with_name("run_initial_eval.py")


def load_orchestrator():
    spec = importlib.util.spec_from_file_location("run_initial_eval", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class RunInitialEvalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.orchestrator = load_orchestrator()
        self.commands: list[list[str]] = []

    def fake_run(self, command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        self.commands.append(command)
        return subprocess.CompletedProcess(command, 0, "", "")

    def script_names(self) -> list[str]:
        return [Path(command[1]).name for command in self.commands]

    def test_runs_bucket_commands_in_order_with_passthrough_options(self) -> None:
        with patch.object(self.orchestrator.subprocess, "run", side_effect=self.fake_run):
            result = self.orchestrator.main(
                [
                    "--bucket",
                    "response",
                    "--run-id",
                    "run-one",
                    "--case",
                    "case-response-one",
                    "--model",
                    "gpt-test",
                    "--reasoning",
                    "medium",
                    "--timeout-seconds",
                    "44",
                    "--rerun",
                    "--skip-exec",
                ]
            )

        self.assertEqual(result, 0)
        self.assertEqual(
            self.script_names(),
            [
                "run_eval_bucket.py",
                "evaluate_eval_run.py",
                "validate_eval_run.py",
                "render_eval_review_html.py",
            ],
        )
        runner, evaluator, validator, renderer = self.commands
        self.assertEqual(runner[0], sys.executable)
        self.assertIn("--bucket", runner)
        self.assertIn("response", runner)
        self.assertIn("--run-id", runner)
        self.assertIn("run-one", runner)
        self.assertIn("--case", runner)
        self.assertIn("case-response-one", runner)
        self.assertIn("--model", runner)
        self.assertIn("gpt-test", runner)
        self.assertIn("--reasoning", runner)
        self.assertIn("medium", runner)
        self.assertIn("--timeout-seconds", runner)
        self.assertIn("44", runner)
        self.assertIn("--rerun", runner)
        self.assertIn("--skip-exec", runner)
        self.assertIn("--model", evaluator)
        self.assertIn("gpt-test", evaluator)
        self.assertIn("--reasoning", evaluator)
        self.assertIn("high", evaluator)
        self.assertNotIn("--skip-oracle", validator)
        self.assertNotIn("--case", renderer)

    def test_render_only_skips_runner_and_evaluator_and_relaxes_validator_oracle(self) -> None:
        with patch.object(self.orchestrator.subprocess, "run", side_effect=self.fake_run):
            result = self.orchestrator.main(
                [
                    "--bucket",
                    "response",
                    "--run-id",
                    "run-one",
                    "--render-only",
                ]
            )

        self.assertEqual(result, 0)
        self.assertEqual(
            self.script_names(),
            ["validate_eval_run.py", "render_eval_review_html.py"],
        )
        self.assertIn("--skip-oracle", self.commands[0])

    def test_skip_oracle_skips_evaluator_and_passes_validator_flag(self) -> None:
        with patch.object(self.orchestrator.subprocess, "run", side_effect=self.fake_run):
            result = self.orchestrator.main(
                [
                    "--bucket",
                    "response",
                    "--run-id",
                    "run-one",
                    "--skip-oracle",
                ]
            )

        self.assertEqual(result, 0)
        self.assertEqual(
            self.script_names(),
            ["run_eval_bucket.py", "validate_eval_run.py", "render_eval_review_html.py"],
        )
        self.assertIn("--skip-oracle", self.commands[1])

    def test_evaluator_model_can_be_overridden(self) -> None:
        with patch.object(self.orchestrator.subprocess, "run", side_effect=self.fake_run):
            result = self.orchestrator.main(
                [
                    "--bucket",
                    "response",
                    "--run-id",
                    "run-one",
                    "--model",
                    "gpt-runner",
                    "--evaluator-model",
                    "gpt-evaluator",
                    "--evaluator-reasoning",
                    "medium",
                ]
            )

        self.assertEqual(result, 0)
        evaluator = self.commands[1]
        self.assertIn("--model", evaluator)
        self.assertIn("gpt-evaluator", evaluator)
        self.assertIn("--reasoning", evaluator)
        self.assertIn("medium", evaluator)

    def test_keep_going_continues_later_buckets_but_returns_nonzero(self) -> None:
        def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            self.commands.append(command)
            returncode = 9 if Path(command[1]).name == "run_eval_bucket.py" and "response" in command else 0
            return subprocess.CompletedProcess(command, returncode, "", "")

        with patch.object(self.orchestrator.subprocess, "run", side_effect=fake_run):
            result = self.orchestrator.main(
                [
                    "--bucket",
                    "response",
                    "--bucket",
                    "code",
                    "--run-id",
                    "run-one",
                    "--keep-going",
                ]
            )

        self.assertEqual(result, 1)
        self.assertEqual(
            [
                (Path(command[1]).name, command[command.index("--bucket") + 1])
                for command in self.commands
            ],
            [
                ("run_eval_bucket.py", "response"),
                ("run_eval_bucket.py", "code"),
                ("evaluate_eval_run.py", "code"),
                ("validate_eval_run.py", "code"),
                ("render_eval_review_html.py", "code"),
            ],
        )

    def test_without_keep_going_stops_on_first_failure(self) -> None:
        def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            self.commands.append(command)
            return subprocess.CompletedProcess(command, 9, "", "")

        with patch.object(self.orchestrator.subprocess, "run", side_effect=fake_run):
            result = self.orchestrator.main(
                [
                    "--bucket",
                    "response",
                    "--bucket",
                    "code",
                    "--run-id",
                    "run-one",
                ]
            )

        self.assertEqual(result, 1)
        self.assertEqual(self.script_names(), ["run_eval_bucket.py"])

    def test_unsafe_run_ids_are_rejected(self) -> None:
        for run_id in ("../escape", "nested/run", "/tmp/escape", "two\\parts", ""):
            with self.subTest(run_id=run_id):
                with self.assertRaisesRegex(SystemExit, "unsafe run id"):
                    self.orchestrator.main(["--bucket", "response", "--run-id", run_id])


if __name__ == "__main__":
    unittest.main()
