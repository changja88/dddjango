#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).with_name("run_initial_eval.py")
RUN_ID_RESPONSE = "20260517-101010-response-try01-full-current-baseline"
RUN_ID_CODE = "20260517-101010-code-try01-full-current-baseline"


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
                    RUN_ID_RESPONSE,
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
        self.assertIn(RUN_ID_RESPONSE, runner)
        self.assertIn("--lv-up-analysis", runner)
        self.assertIn("--lv-up-plan", runner)
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
        self.assertIn("--allow-skipped-exits", validator)
        self.assertNotIn("--case", renderer)

    def test_render_only_skips_runner_and_evaluator_without_relaxing_validator_oracle(self) -> None:
        with patch.object(self.orchestrator.subprocess, "run", side_effect=self.fake_run):
            result = self.orchestrator.main(
                [
                    "--bucket",
                    "response",
                    "--run-id",
                    RUN_ID_RESPONSE,
                    "--render-only",
                ]
            )

        self.assertEqual(result, 0)
        self.assertEqual(
            self.script_names(),
            ["validate_eval_run.py", "render_eval_review_html.py"],
        )
        self.assertNotIn("--skip-oracle", self.commands[0])
        self.assertNotIn("--allow-skipped-exits", self.commands[0])

    def test_render_only_with_explicit_skip_oracle_passes_validator_flag(self) -> None:
        with patch.object(self.orchestrator.subprocess, "run", side_effect=self.fake_run):
            result = self.orchestrator.main(
                [
                    "--bucket",
                    "response",
                    "--run-id",
                    RUN_ID_RESPONSE,
                    "--render-only",
                    "--skip-oracle",
                ]
            )

        self.assertEqual(result, 0)
        self.assertEqual(
            self.script_names(),
            ["validate_eval_run.py", "render_eval_review_html.py"],
        )
        self.assertIn("--skip-oracle", self.commands[0])
        self.assertNotIn("--allow-skipped-exits", self.commands[0])

    def test_skip_oracle_skips_evaluator_and_passes_validator_flag(self) -> None:
        with patch.object(self.orchestrator.subprocess, "run", side_effect=self.fake_run):
            result = self.orchestrator.main(
                [
                    "--bucket",
                    "response",
                    "--run-id",
                    RUN_ID_RESPONSE,
                    "--skip-oracle",
                ]
            )

        self.assertEqual(result, 0)
        self.assertEqual(
            self.script_names(),
            ["run_eval_bucket.py", "validate_eval_run.py", "render_eval_review_html.py"],
        )
        self.assertIn("--skip-oracle", self.commands[1])
        self.assertNotIn("--allow-skipped-exits", self.commands[1])

    def test_skip_exec_skip_oracle_allows_skipped_exit_validation(self) -> None:
        with patch.object(self.orchestrator.subprocess, "run", side_effect=self.fake_run):
            result = self.orchestrator.main(
                [
                    "--bucket",
                    "response",
                    "--run-id",
                    RUN_ID_RESPONSE,
                    "--skip-exec",
                    "--skip-oracle",
                ]
            )

        self.assertEqual(result, 0)
        self.assertEqual(
            self.script_names(),
            ["run_eval_bucket.py", "validate_eval_run.py", "render_eval_review_html.py"],
        )
        validator = self.commands[1]
        self.assertIn("--skip-oracle", validator)
        self.assertIn("--allow-skipped-exits", validator)

    def test_evaluator_model_can_be_overridden(self) -> None:
        with patch.object(self.orchestrator.subprocess, "run", side_effect=self.fake_run):
            result = self.orchestrator.main(
                [
                    "--bucket",
                    "response",
                    "--run-id",
                    RUN_ID_RESPONSE,
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

    def test_case_jobs_runs_case_pipelines_in_parallel_then_full_validate_and_render(self) -> None:
        cases = [
            Path("/eval/response/cases/plugin/public/case-response-one.md"),
            Path("/eval/response/cases/plugin/public/case-response-two.md"),
        ]
        with patch.object(self.orchestrator.common, "selected_case_paths", return_value=cases):
            with patch.object(self.orchestrator.subprocess, "run", side_effect=self.fake_run):
                result = self.orchestrator.main(
                    [
                        "--bucket",
                        "response",
                        "--run-id",
                        RUN_ID_RESPONSE,
                        "--case-jobs",
                        "2",
                    ]
                )

        self.assertEqual(result, 0)
        self.assertEqual(self.script_names().count("run_eval_bucket.py"), 2)
        self.assertEqual(self.script_names().count("evaluate_eval_run.py"), 2)
        self.assertEqual(self.script_names().count("validate_eval_run.py"), 3)
        self.assertEqual(self.script_names().count("render_eval_review_html.py"), 1)

        case_commands = [
            command
            for command in self.commands
            if Path(command[1]).name
            in {"run_eval_bucket.py", "evaluate_eval_run.py", "validate_eval_run.py"}
            and "--case" in command
        ]
        rendered = [
            command for command in self.commands if Path(command[1]).name == "render_eval_review_html.py"
        ]
        full_validators = [
            command
            for command in self.commands
            if Path(command[1]).name == "validate_eval_run.py" and "--case" not in command
        ]
        seen_cases = {
            command[command.index("--case") + 1]
            for command in case_commands
        }
        self.assertEqual(seen_cases, {"case-response-one", "case-response-two"})
        self.assertEqual(len(full_validators), 1)
        self.assertEqual(len(rendered), 1)
        self.assertNotIn("--case", rendered[0])

    def test_case_jobs_must_be_positive(self) -> None:
        with self.assertRaisesRegex(SystemExit, "case-jobs must be positive"):
            self.orchestrator.main(["--bucket", "response", "--run-id", RUN_ID_RESPONSE, "--case-jobs", "0"])

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
                ]
            )

        self.assertEqual(result, 1)
        self.assertEqual(self.script_names(), ["run_eval_bucket.py"])

    def test_invalid_run_ids_are_rejected(self) -> None:
        for run_id in ("../escape", "nested/run", "/tmp/escape", "two\\parts", "", "run-one"):
            with self.subTest(run_id=run_id):
                with self.assertRaisesRegex(SystemExit, "Invalid run id"):
                    self.orchestrator.main(["--bucket", "response", "--run-id", run_id])

    def test_explicit_run_id_with_multiple_buckets_is_rejected(self) -> None:
        with self.assertRaisesRegex(SystemExit, "explicit --run-id can only be used with one bucket"):
            self.orchestrator.main(
                ["--bucket", "response", "--bucket", "code", "--run-id", RUN_ID_RESPONSE]
            )

    def test_run_id_generated_per_bucket_when_explicit_run_id_is_missing(self) -> None:
        with patch.object(self.orchestrator.subprocess, "run", side_effect=self.fake_run):
            result = self.orchestrator.main(
                [
                    "--bucket",
                    "response",
                    "--bucket",
                    "code",
                    "--try-number",
                    "2",
                    "--scope",
                    "targeted",
                    "--topic",
                    "pilot",
                ]
            )

        self.assertEqual(result, 0)
        seen_run_ids = {
            command[command.index("--bucket") + 1]: command[command.index("--run-id") + 1]
            for command in self.commands
            if "--run-id" in command and Path(command[1]).name == "run_eval_bucket.py"
        }
        self.assertEqual(set(seen_run_ids), {"response", "code"})
        self.assertNotEqual(seen_run_ids["response"], seen_run_ids["code"])
        self.assertIn("-response-try02-targeted-pilot", seen_run_ids["response"])
        self.assertIn("-code-try02-targeted-pilot", seen_run_ids["code"])

    def test_explicit_run_id_bucket_mismatch_is_rejected(self) -> None:
        with self.assertRaisesRegex(SystemExit, "run id bucket=code"):
            self.orchestrator.main(["--bucket", "response", "--run-id", RUN_ID_CODE])


if __name__ == "__main__":
    unittest.main()
