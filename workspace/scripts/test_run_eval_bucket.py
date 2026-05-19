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
        answer_text: str | None = None,
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
        if answer_text is None:
            answer_text = f"id: {case_id}\ncase_id: {case_id}\nbucket: {bucket}\nkind: {bucket}\n"
            if bucket == "code":
                answer_text += "code_expected: true\ndeterministic_checks: []\n"
        answer_path.write_text(answer_text, encoding="utf-8")

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

    def test_run_command_prefers_current_interpreter_bin_on_path(self) -> None:
        with patch.object(self.runner.subprocess, "run") as run:
            run.return_value = subprocess.CompletedProcess(["python3", "--version"], 0, "", "")

            self.runner.run_command(
                ["python3", "--version"],
                prompt=None,
                cwd=self.root,
                timeout_seconds=10,
            )

        env = run.call_args.kwargs["env"]
        self.assertTrue(env["PATH"].startswith(str(Path(sys.executable).parent)))

    def init_git_workspace(self, workspace: Path) -> None:
        workspace.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "init"], cwd=workspace, check=True, capture_output=True, text=True)
        subprocess.run(
            ["git", "config", "user.name", "Eval Test"],
            cwd=workspace,
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "eval-test@example.invalid"],
            cwd=workspace,
            check=True,
            capture_output=True,
            text=True,
        )
        (workspace / "README.md").write_text("fixture\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=workspace, check=True, capture_output=True, text=True)
        subprocess.run(
            ["git", "commit", "-m", "initial"],
            cwd=workspace,
            check=True,
            capture_output=True,
            text=True,
        )

    def test_skip_exec_writes_required_raw_artifacts_for_both_variants(self) -> None:
        self.write_case()

        result = self.runner.main(
            [
                "--bucket",
                "response",
                "--run-id",
                "20260517-143012-response-try01-full-current-baseline",
                "--workspace-root",
                str(self.workspace_root),
                "--skip-exec",
            ]
        )

        self.assertEqual(result, 0)
        raw = self.runner.common.EVAL_ROOT / "response/runs/20260517-143012-response-try01-full-current-baseline/raw"
        with_variant = self.runner.common.VARIANTS[1]
        for name in (
            "case-response-one-public-prompt.md",
            "case-response-one-operator-prompt.txt",
            f"case-response-one-{with_variant}-prompt-input.json",
            f"case-response-one-{with_variant}-prompt-input.stderr.txt",
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
        self.assertFalse((raw / "case-response-one-baseline-prompt-input.stderr.txt").exists())
        prompt_input = json.loads(
            (raw / f"case-response-one-{with_variant}-prompt-input.json").read_text(encoding="utf-8")
        )
        self.assertEqual(prompt_input, {"skipped": True, "reason": "--skip-exec"})
        self.assertEqual(
            (raw / f"case-response-one-{with_variant}-prompt-input.stderr.txt").read_text(
                encoding="utf-8"
            ),
            "",
        )
        isolation = json.loads((raw / "case-response-one-baseline-isolation.json").read_text(encoding="utf-8"))
        self.assertTrue(isolation["commandUsesIgnoreUserConfig"])
        self.assertTrue(isolation["forbiddenPathsAbsent"])

    def test_baseline_only_still_writes_with_ddjango_prompt_input_debug_artifacts(self) -> None:
        self.write_case()
        self.commands = []

        with patch.object(self.runner, "run_command", side_effect=self.fake_run_command):
            result = self.runner.main(
                [
                    "--bucket",
                    "response",
                    "--run-id",
                    "20260517-143013-response-try01-targeted-case-response-one",
                    "--case",
                    "case-response-one",
                    "--variant",
                    "baseline",
                    "--workspace-root",
                    str(self.workspace_root),
                ]
            )

        self.assertEqual(result, 1)
        raw = self.runner.common.EVAL_ROOT / "response/runs/20260517-143013-response-try01-targeted-case-response-one/raw"
        with_variant = self.runner.common.VARIANTS[1]
        self.assertTrue((raw / f"case-response-one-{with_variant}-prompt-input.json").is_file())
        self.assertTrue(
            (raw / f"case-response-one-{with_variant}-prompt-input.stderr.txt").is_file()
        )
        self.assertFalse((raw / "case-response-one-baseline-prompt-input.json").exists())
        self.assertFalse((raw / "case-response-one-baseline-prompt-input.stderr.txt").exists())
        debug_commands = [
            command for command, _prompt, _cwd, _timeout_seconds in self.commands
            if command[:3] == ["codex", "debug", "prompt-input"]
        ]
        self.assertEqual(len(debug_commands), 1)

    def test_exec_mode_writes_command_exit_stdout_and_stderr_artifacts(self) -> None:
        self.write_case()
        self.commands = []

        with patch.object(self.runner, "run_command", side_effect=self.fake_run_command):
            result = self.runner.main(
                [
                    "--bucket",
                    "response",
                    "--run-id",
                    "20260517-143014-response-try01-full-exec-mode",
                    "--case",
                    "case-response-one",
                    "--workspace-root",
                    str(self.workspace_root),
                ]
            )

        self.assertEqual(result, 1)
        raw = self.runner.common.EVAL_ROOT / "response/runs/20260517-143014-response-try01-full-exec-mode/raw"
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
        self.assertIn("--json", baseline_command)
        self.assertIn("--json", with_ddjango_command)
        self.assertIn("--ignore-user-config", baseline_command)
        self.assertIn("--ignore-rules", baseline_command)
        self.assertNotIn("--ignore-user-config", with_ddjango_command)
        self.assertNotIn("--ignore-rules", with_ddjango_command)
        self.assertTrue((raw / f"case-response-one-{with_variant}-prompt-input.json").is_file())
        self.assertFalse((raw / "case-response-one-baseline-prompt-input.json").exists())

    def test_fixed_shape_answer_prompt_does_not_force_command_footer(self) -> None:
        prompt = self.runner.build_prompt(
            "핵심 설계 결정만 5개 bullet로 끝내줘.\n",
            allow_workspace_edits=False,
        )

        self.assertNotIn("include commands actually run plus checks not run", prompt)
        self.assertNotIn("If a check is not actually run, state that it was not run.", prompt)
        self.assertIn("Preserve the requested answer shape exactly.", prompt)
        self.assertIn("do not add command, check, tool, or verification notes", prompt)

    def test_brief_answer_prompt_does_not_force_command_footer(self) -> None:
        prompt = self.runner.build_prompt(
            "migration 영향만 짧게 답해줘.\n",
            allow_workspace_edits=False,
        )

        self.assertNotIn("include commands actually run plus checks not run", prompt)
        self.assertNotIn("If a check is not actually run, state that it was not run.", prompt)
        self.assertIn("Preserve the requested brevity.", prompt)
        self.assertIn("Do not claim checks, tests, file inspection, or command execution unless actually run.", prompt)

    def test_open_shape_answer_prompt_keeps_honesty_without_internal_command_footer(self) -> None:
        prompt = self.runner.build_prompt(
            "주문 생성 workflow를 검토해줘.\n",
            allow_workspace_edits=False,
            bucket="response",
        )

        self.assertNotIn("include commands actually run plus checks not run", prompt)
        self.assertIn("If a relevant check is not actually run, state that it was not run.", prompt)
        self.assertIn("Do not print local absolute paths", prompt)
        self.assertIn("agent-internal skill-loading commands", prompt)

    def test_runtime_prompt_requires_read_only_evidence_without_local_path_reporting(self) -> None:
        prompt = self.runner.build_prompt(
            "runtime cache와 bundled reference를 확인해줘.\n",
            allow_workspace_edits=False,
            bucket="runtime",
        )

        self.assertIn("Runtime bucket evidence policy:", prompt)
        self.assertIn("Run feasible read-only inspections", prompt)
        self.assertIn("runtime/cache/source comparison", prompt)
        self.assertIn("visible prompt skill metadata", prompt)
        self.assertIn("installed/cache metadata evidence", prompt)
        self.assertIn("workspace/develop/eval/runtime/fixtures/current-run", prompt)
        self.assertIn("Do not print local absolute paths", prompt)
        self.assertIn("agent-internal skill-loading commands", prompt)
        self.assertNotIn("include commands actually run plus checks not run", prompt)

    def test_copies_current_run_runtime_evidence_only_for_with_ddjango(self) -> None:
        raw_dir = Path(self.tmp.name) / "raw"
        raw_dir.mkdir()
        workspace = Path(self.tmp.name) / "workspace"
        workspace.mkdir()
        case_id = "case-runtime-one"
        expected_files = [
            f"{case_id}-with-dddjango-prompt-input.json",
            f"{case_id}-with-dddjango-prompt-input.stderr.txt",
            f"{case_id}-baseline-isolation.json",
        ]
        for filename in expected_files:
            (raw_dir / filename).write_text(f"{filename}\n", encoding="utf-8")

        self.runner.copy_runtime_current_run_evidence(
            raw_dir=raw_dir,
            workspace=workspace,
            case_id=case_id,
            bucket="runtime",
            variant=self.runner.VARIANT_CONFIG["with-dddjango"],
        )

        evidence_dir = workspace / "workspace/develop/eval/runtime/fixtures/current-run"
        self.assertTrue(evidence_dir.is_dir())
        for filename in expected_files:
            self.assertEqual(
                (evidence_dir / filename).read_text(encoding="utf-8"),
                f"{filename}\n",
            )

    def test_does_not_copy_current_run_runtime_evidence_for_baseline_or_other_buckets(self) -> None:
        raw_dir = Path(self.tmp.name) / "raw"
        raw_dir.mkdir()
        workspace = Path(self.tmp.name) / "workspace"
        workspace.mkdir()
        case_id = "case-runtime-one"
        (raw_dir / f"{case_id}-with-dddjango-prompt-input.json").write_text(
            '{"messages":[]}\n',
            encoding="utf-8",
        )

        self.runner.copy_runtime_current_run_evidence(
            raw_dir=raw_dir,
            workspace=workspace,
            case_id=case_id,
            bucket="runtime",
            variant=self.runner.VARIANT_CONFIG["baseline"],
        )
        self.runner.copy_runtime_current_run_evidence(
            raw_dir=raw_dir,
            workspace=workspace,
            case_id=case_id,
            bucket="response",
            variant=self.runner.VARIANT_CONFIG["with-dddjango"],
        )

        evidence_dir = workspace / "workspace/develop/eval/runtime/fixtures/current-run"
        self.assertFalse(evidence_dir.exists())

    def test_response_prompt_does_not_use_runtime_evidence_policy(self) -> None:
        prompt = self.runner.build_prompt(
            "runtime cache와 bundled reference를 확인해줘.\n",
            allow_workspace_edits=False,
            bucket="response",
        )

        self.assertNotIn("Runtime bucket evidence policy:", prompt)
        self.assertIn("If a relevant check is not actually run, state that it was not run.", prompt)
        self.assertNotIn("include commands actually run plus checks not run", prompt)

    def test_runtime_bucket_operator_prompt_uses_runtime_evidence_policy(self) -> None:
        self.write_case(bucket="runtime", case_id="case-runtime-one")

        result = self.runner.main(
            [
                    "--bucket",
                    "runtime",
                    "--run-id",
                    "20260517-143015-runtime-try01-full-current-baseline",
                "--case",
                "case-runtime-one",
                "--workspace-root",
                str(self.workspace_root),
                "--skip-exec",
            ]
        )

        self.assertEqual(result, 0)
        operator_prompt = (
            self.runner.common.EVAL_ROOT
            / "runtime/runs/20260517-143015-runtime-try01-full-current-baseline/raw/case-runtime-one-operator-prompt.txt"
        ).read_text(encoding="utf-8")
        self.assertIn("Runtime bucket evidence policy:", operator_prompt)
        self.assertIn("Do not print local absolute paths", operator_prompt)

    def test_workflow_bucket_writes_trace_marker_and_skipped_trace_artifacts(self) -> None:
        self.write_case(bucket="workflow", case_id="case-workflow-one")

        result = self.runner.main(
            [
                "--bucket",
                "workflow",
                "--run-id",
                "20260517-143016-workflow-try01-full-current-baseline",
                "--case",
                "case-workflow-one",
                "--workspace-root",
                str(self.workspace_root),
                "--skip-exec",
            ]
        )

        self.assertEqual(result, 0)
        run_dir = self.runner.common.EVAL_ROOT / "workflow/runs/20260517-143016-workflow-try01-full-current-baseline"
        marker = json.loads((run_dir / "SUBAGENT_TRACE_CAPTURE.json").read_text(encoding="utf-8"))
        self.assertEqual(marker["bucket"], "workflow")
        self.assertFalse(marker["stderrUsedForClaims"])
        raw = run_dir / "raw"
        for variant in self.runner.common.VARIANTS:
            trace_path = raw / f"case-workflow-one-{variant}-subagent-trace.json"
            self.assertTrue(trace_path.is_file(), trace_path)
            trace = json.loads(trace_path.read_text(encoding="utf-8"))
            self.assertEqual(trace["caseId"], "case-workflow-one")
            self.assertEqual(trace["variant"], variant)
            self.assertEqual(trace["traceStatus"], "skipped")
            self.assertEqual(trace["responseSource"], f"raw/case-workflow-one-{variant}.txt")

    def test_workflow_bucket_regenerates_missing_trace_for_skipped_existing_output(self) -> None:
        self.write_case(bucket="workflow", case_id="case-workflow-one")
        raw = self.runner.common.EVAL_ROOT / "workflow/runs/20260517-143017-workflow-try01-targeted-case-workflow-one/raw"
        raw.mkdir(parents=True, exist_ok=True)
        for variant in self.runner.common.VARIANTS:
            (raw / f"case-workflow-one-{variant}.txt").write_text(
                "subagent는 사용하지 않고 순차 검토했습니다.\n",
                encoding="utf-8",
            )
            (raw / f"case-workflow-one-{variant}-events.jsonl").write_text("", encoding="utf-8")
            (raw / f"case-workflow-one-{variant}-exit.txt").write_text("0\n", encoding="utf-8")

        result = self.runner.main(
            [
                    "--bucket",
                    "workflow",
                    "--run-id",
                    "20260517-143017-workflow-try01-targeted-case-workflow-one",
                "--case",
                "case-workflow-one",
                "--workspace-root",
                str(self.workspace_root),
            ]
        )

        self.assertEqual(result, 0)
        for variant in self.runner.common.VARIANTS:
            trace = json.loads(
                (raw / f"case-workflow-one-{variant}-subagent-trace.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(trace["traceStatus"], "fallback-stated")

    def test_code_bucket_rejects_case_without_capture_code_enabled(self) -> None:
        self.write_case(bucket="code", case_id="case-code-one")
        self.write_code_capture_metadata(capture_code=False)

        with self.assertRaisesRegex(SystemExit, "captureCode: true"):
            self.runner.main(
                [
                    "--bucket",
                    "code",
                    "--run-id",
                    "20260517-143018-code-try01-full-current-baseline",
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
                "20260517-143019-code-try01-targeted-case-code-one",
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
        run_dir = self.runner.common.EVAL_ROOT / "code/runs/20260517-143019-code-try01-targeted-case-code-one"
        self.assertTrue((run_dir / "code/case-code-one/baseline/changed-files.json").is_file())
        self.assertTrue((run_dir / "code/case-code-one/baseline/diff.patch").is_file())
        command = (run_dir / "raw/case-code-one-baseline-command.txt").read_text(encoding="utf-8")
        self.assertIn("-s workspace-write", command)

    def test_code_bucket_skip_exec_records_deterministic_check_artifacts(self) -> None:
        self.write_case(
            bucket="code",
            case_id="case-code-one",
            answer_text=(
                "id: case-code-one\n"
                "case_id: case-code-one\n"
                "bucket: code\n"
                "kind: code\n"
                "code_expected: true\n"
                "deterministic_checks:\n"
                "  - id: unit-tests\n"
                "    command: python3 -m unittest\n"
                "    expected_exit: 0\n"
                "    evidence: command-artifact\n"
            ),
        )
        self.write_code_capture_metadata()

        result = self.runner.main(
            [
                "--bucket",
                "code",
                "--run-id",
                "20260517-143022-code-try01-targeted-case-code-one",
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
        checks = (
            self.runner.common.EVAL_ROOT
            / "code/runs/20260517-143022-code-try01-targeted-case-code-one/code/case-code-one/baseline/checks"
        )
        self.assertEqual(
            (checks / "unit-tests-command.txt").read_text(encoding="utf-8"),
            "python3 -m unittest\n",
        )
        self.assertEqual((checks / "unit-tests-exit.txt").read_text(encoding="utf-8"), "0\n")
        self.assertTrue((checks / "unit-tests-stdout.txt").is_file())
        self.assertTrue((checks / "unit-tests-stderr.txt").is_file())

    def test_code_bucket_records_behavior_check_with_workspace_from_repo_root(self) -> None:
        self.write_case(
            bucket="code",
            case_id="case-code-one",
            answer_text=(
                "id: case-code-one\n"
                "case_id: case-code-one\n"
                "bucket: code\n"
                "kind: code\n"
                "code_expected: true\n"
                "deterministic_checks: []\n"
                "behavior_checks:\n"
                "  - id: hidden\n"
                "    command: python3 workspace/scripts/eval_code_behavior_checks.py --case case-code-one\n"
                "    expected_exit: 0\n"
            ),
        )
        self.write_code_capture_metadata()
        self.commands = []

        with patch.object(self.runner, "run_command", side_effect=self.fake_run_command):
            result = self.runner.main(
                [
                    "--bucket",
                    "code",
                    "--run-id",
                    "20260517-143023-code-try01-targeted-case-code-one",
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
        run_dir = self.runner.common.EVAL_ROOT / "code/runs/20260517-143023-code-try01-targeted-case-code-one"
        checks = run_dir / "code/case-code-one/baseline/behavior-checks"
        command_text = (checks / "hidden-command.txt").read_text(encoding="utf-8")
        self.assertIn("workspace/scripts/eval_code_behavior_checks.py", command_text)
        self.assertIn("--workspace", command_text)
        self.assertEqual((checks / "hidden-exit.txt").read_text(encoding="utf-8"), "0\n")
        behavior_commands = [
            (command, cwd)
            for command, _prompt, cwd, _timeout_seconds in self.commands
            if "workspace/scripts/eval_code_behavior_checks.py" in command
        ]
        self.assertEqual(len(behavior_commands), 1)
        command, cwd = behavior_commands[0]
        self.assertEqual(cwd, self.root)
        self.assertIn("--workspace", command)

    def test_code_bucket_behavior_check_failure_does_not_abort_run(self) -> None:
        self.write_case(
            bucket="code",
            case_id="case-code-one",
            answer_text=(
                "id: case-code-one\n"
                "case_id: case-code-one\n"
                "bucket: code\n"
                "kind: code\n"
                "code_expected: true\n"
                "deterministic_checks: []\n"
                "behavior_checks:\n"
                "  - id: hidden\n"
                "    command: python3 workspace/scripts/eval_code_behavior_checks.py --case case-code-one\n"
                "    expected_exit: 0\n"
            ),
        )
        self.write_code_capture_metadata()

        def fake_run_command(command, *, prompt, cwd, timeout_seconds):
            if "workspace/scripts/eval_code_behavior_checks.py" in command:
                return subprocess.CompletedProcess(command, 1, "", "quality failure\n")
            return self.fake_run_command(command, prompt=prompt, cwd=cwd, timeout_seconds=timeout_seconds)

        self.commands = []
        with patch.object(self.runner, "run_command", side_effect=fake_run_command):
            result = self.runner.main(
                [
                    "--bucket",
                    "code",
                    "--run-id",
                    "20260517-143024-code-try01-targeted-case-code-one",
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
        checks = (
            self.runner.common.EVAL_ROOT
            / "code/runs/20260517-143024-code-try01-targeted-case-code-one/code/case-code-one/baseline/behavior-checks"
        )
        self.assertEqual((checks / "hidden-exit.txt").read_text(encoding="utf-8"), "1\n")
        self.assertEqual(
            (checks / "hidden-stderr.txt").read_text(encoding="utf-8"),
            "quality failure\n",
        )

    def test_capture_code_artifacts_lists_untracked_nested_files_individually(self) -> None:
        workspace = Path(self.tmp.name) / "code-workspace"
        run_dir = Path(self.tmp.name) / "run"
        self.init_git_workspace(workspace)
        nested_file = workspace / "new_package" / "nested" / "created.py"
        nested_file.parent.mkdir(parents=True)
        nested_file.write_text("print('created')\n", encoding="utf-8")

        self.runner.capture_code_artifacts(workspace, run_dir, "case-code-one", "baseline")

        manifest_path = run_dir / "code/case-code-one/baseline/changed-files.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        files = manifest["files"]
        self.assertEqual([entry["path"] for entry in files], ["new_package/nested/created.py"])
        copied_file = run_dir / files[0]["artifactPath"]
        self.assertTrue(copied_file.is_file())
        self.assertEqual(copied_file.read_text(encoding="utf-8"), "print('created')\n")

    def test_capture_code_artifacts_writes_quality_policy_findings(self) -> None:
        workspace = Path(self.tmp.name) / "policy-workspace"
        run_dir = Path(self.tmp.name) / "run-policy"
        self.init_git_workspace(workspace)
        changed_file = workspace / "app.py"
        changed_file.write_text("print('outside allowed paths')\n", encoding="utf-8")
        answer_text = (
            "id: case-code-one\n"
            "case_id: case-code-one\n"
            "bucket: code\n"
            "kind: code\n"
            "code_expected: true\n"
            "deterministic_checks: []\n"
            "allowed_paths:\n"
            "  - apps/orders/**\n"
            "forbidden_paths:\n"
            "  - workspace/develop/eval/**\n"
        )

        self.runner.capture_code_artifacts(
            workspace,
            run_dir,
            "case-code-one",
            "baseline",
            answer_text=answer_text,
        )

        policy = json.loads(
            (
                run_dir / "code/case-code-one/baseline/policy-findings.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(
            policy["findings"],
            [
                {
                    "severity": "quality",
                    "rule": "allowed_paths",
                    "path": "app.py",
                    "message": "changed path is outside scoring allowed_paths: app.py",
                    "allowedPaths": ["apps/orders/**"],
                }
            ],
        )

    def test_deleted_file_manifest_does_not_require_copied_source_artifact(self) -> None:
        workspace = Path(self.tmp.name) / "delete-workspace"
        run_dir = Path(self.tmp.name) / "run-delete"
        self.init_git_workspace(workspace)
        tracked_file = workspace / "obsolete.py"
        tracked_file.write_text("print('remove me')\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=workspace, check=True, capture_output=True, text=True)
        subprocess.run(
            ["git", "commit", "-m", "add obsolete"],
            cwd=workspace,
            check=True,
            capture_output=True,
            text=True,
        )
        tracked_file.unlink()

        self.runner.capture_code_artifacts(workspace, run_dir, "case-code-one", "baseline")

        manifest_path = run_dir / "code/case-code-one/baseline/changed-files.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(len(manifest["files"]), 1)
        entry = manifest["files"][0]
        self.assertEqual(entry["path"], "obsolete.py")
        self.assertEqual(entry["status"], "deleted")
        self.assertTrue(entry["binary"])
        self.assertEqual(entry["artifactPath"], "")

    def test_prepare_isolated_workspace_removes_lv_up_plan_artifacts(self) -> None:
        lv_up_file = self.root / "workspace/develop/lv_up_plan/runtime/review/note.md"
        lv_up_file.parent.mkdir(parents=True)
        lv_up_file.write_text("runtime improvement notes\n", encoding="utf-8")

        workspace = self.runner.prepare_isolated_workspace(
            source_repo=self.root,
            workspace_root=self.workspace_root,
            run_id="20260517-143020-runtime-try01-full-current-baseline",
            case_id="case-runtime-one",
            variant=self.runner.VARIANT_CONFIG["with-dddjango"],
        )

        self.assertFalse((workspace / "workspace/develop/lv_up_plan").exists())

    def test_previous_skip_exec_output_does_not_skip_later_execution(self) -> None:
        self.write_case()
        skip_result = self.runner.main(
            [
                "--bucket",
                "response",
                "--run-id",
                "20260517-143021-response-try01-full-after-skip",
                "--case",
                "case-response-one",
                "--variant",
                "baseline",
                "--workspace-root",
                str(self.workspace_root),
                "--skip-exec",
            ]
        )
        self.assertEqual(skip_result, 0)
        self.commands = []

        with patch.object(self.runner, "run_command", side_effect=self.fake_run_command):
            result = self.runner.main(
                [
                    "--bucket",
                    "response",
                    "--run-id",
                    "20260517-143021-response-try01-full-after-skip",
                    "--case",
                    "case-response-one",
                    "--variant",
                    "baseline",
                    "--workspace-root",
                    str(self.workspace_root),
                ]
            )

        self.assertEqual(result, 1)
        exec_commands = [command for command, _prompt, _cwd, _timeout in self.commands if "exec" in command]
        self.assertEqual(len(exec_commands), 1)
        raw = self.runner.common.EVAL_ROOT / "response/runs/20260517-143021-response-try01-full-after-skip/raw"
        self.assertEqual((raw / "case-response-one-baseline-exit.txt").read_text(encoding="utf-8"), "7\n")

    def test_skipped_existing_failed_output_keeps_parent_exit_nonzero(self) -> None:
        self.write_case()
        raw = self.runner.common.EVAL_ROOT / "response/runs/20260517-143022-response-try01-full-existing-failed/raw"
        raw.mkdir(parents=True)
        (raw / "case-response-one-baseline.txt").write_text(
            "previous failed response\n",
            encoding="utf-8",
        )
        (raw / "case-response-one-baseline-exit.txt").write_text("7\n", encoding="utf-8")
        self.commands = []

        with patch.object(self.runner, "run_command", side_effect=self.fake_run_command):
            result = self.runner.main(
                [
                    "--bucket",
                    "response",
                    "--run-id",
                    "20260517-143022-response-try01-full-existing-failed",
                    "--case",
                    "case-response-one",
                    "--variant",
                    "baseline",
                    "--workspace-root",
                    str(self.workspace_root),
                ]
            )

        self.assertEqual(result, 1)
        exec_commands = [command for command, _prompt, _cwd, _timeout in self.commands if "exec" in command]
        self.assertEqual(exec_commands, [])

    def test_existing_output_without_exit_artifact_is_rerun(self) -> None:
        self.write_case()
        raw = self.runner.common.EVAL_ROOT / "response/runs/20260517-143023-response-try01-full-missing-exit/raw"
        raw.mkdir(parents=True)
        (raw / "case-response-one-baseline.txt").write_text(
            "partial previous response\n",
            encoding="utf-8",
        )
        self.commands = []

        with patch.object(self.runner, "run_command", side_effect=self.fake_run_command):
            result = self.runner.main(
                [
                    "--bucket",
                    "response",
                    "--run-id",
                    "20260517-143023-response-try01-full-missing-exit",
                    "--case",
                    "case-response-one",
                    "--variant",
                    "baseline",
                    "--workspace-root",
                    str(self.workspace_root),
                ]
            )

        self.assertEqual(result, 1)
        exec_commands = [command for command, _prompt, _cwd, _timeout in self.commands if "exec" in command]
        self.assertEqual(len(exec_commands), 1)
        self.assertEqual((raw / "case-response-one-baseline-exit.txt").read_text(encoding="utf-8"), "7\n")

    def test_default_production_run_id_and_run_meta_written(self) -> None:
        self.write_case()

        result = self.runner.main(
            [
                "--bucket",
                "response",
                "--try-number",
                "1",
                "--scope",
                "full",
                "--topic",
                "current-baseline",
                "--workspace-root",
                str(self.workspace_root),
                "--skip-exec",
            ]
        )

        self.assertEqual(result, 0)
        runs_dir = self.runner.common.EVAL_ROOT / "response/runs"
        run_dirs = [path for path in runs_dir.iterdir() if path.is_dir()]
        self.assertEqual(len(run_dirs), 1)
        run_id = run_dirs[0].name
        self.assertRegex(run_id, r"^\d{8}-\d{6}-response-try01-full-current-baseline$")
        meta = json.loads((run_dirs[0] / "RUN_META.json").read_text(encoding="utf-8"))
        self.assertEqual(meta["run_id"], run_id)
        self.assertEqual(meta["bucket"], "response")
        self.assertEqual(meta["try_number"], 1)
        self.assertEqual(meta["scope"], "full")
        self.assertEqual(meta["topic"], "current-baseline")

    def test_invalid_production_run_id_is_rejected(self) -> None:
        self.write_case()
        with self.assertRaisesRegex(SystemExit, "invalid production run id"):
            self.runner.main(
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

    def test_explicit_run_id_bucket_must_match_selected_bucket(self) -> None:
        self.write_case(bucket="response", case_id="case-response-one")
        with self.assertRaisesRegex(
            SystemExit,
            "run id bucket mismatch: run id bucket=runtime, --bucket=response",
        ):
            self.runner.main(
                [
                    "--bucket",
                    "response",
                    "--run-id",
                    "20260517-143012-runtime-try01-full-current-baseline",
                    "--case",
                    "case-response-one",
                    "--workspace-root",
                    str(self.workspace_root),
                    "--skip-exec",
                ]
            )

    def test_unsafe_run_ids_are_rejected(self) -> None:
        self.write_case()
        for run_id in ("../escape", "nested/run", "/tmp/escape"):
            with self.subTest(run_id=run_id):
                with self.assertRaisesRegex(SystemExit, "invalid production run id"):
                    self.runner.main(
                        [
                            "--bucket",
                            "response",
                            "--run-id",
                            run_id,
                            "--case",
                            "case-response-one",
                            "--workspace-root",
                            str(self.workspace_root),
                            "--skip-exec",
                        ]
                    )


if __name__ == "__main__":
    unittest.main()
