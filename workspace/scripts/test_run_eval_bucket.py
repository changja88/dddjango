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
                    "run-baseline-only",
                    "--case",
                    "case-response-one",
                    "--variant",
                    "baseline",
                    "--workspace-root",
                    str(self.workspace_root),
                ]
            )

        self.assertEqual(result, 0)
        raw = self.runner.common.EVAL_ROOT / "response/runs/run-baseline-only/raw"
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

    def test_open_shape_answer_prompt_keeps_command_honesty_footer(self) -> None:
        prompt = self.runner.build_prompt(
            "주문 생성 workflow를 검토해줘.\n",
            allow_workspace_edits=False,
        )

        self.assertIn("include commands actually run plus checks not run", prompt)
        self.assertIn("If a check is not actually run, state that it was not run.", prompt)

    def test_workflow_bucket_writes_trace_marker_and_skipped_trace_artifacts(self) -> None:
        self.write_case(bucket="workflow", case_id="case-workflow-one")

        result = self.runner.main(
            [
                "--bucket",
                "workflow",
                "--run-id",
                "run-workflow",
                "--case",
                "case-workflow-one",
                "--workspace-root",
                str(self.workspace_root),
                "--skip-exec",
            ]
        )

        self.assertEqual(result, 0)
        run_dir = self.runner.common.EVAL_ROOT / "workflow/runs/run-workflow"
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
        raw = self.runner.common.EVAL_ROOT / "workflow/runs/run-workflow/raw"
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
                "run-workflow",
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

    def test_previous_skip_exec_output_does_not_skip_later_execution(self) -> None:
        self.write_case()
        skip_result = self.runner.main(
            [
                "--bucket",
                "response",
                "--run-id",
                "run-after-skip",
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
                    "run-after-skip",
                    "--case",
                    "case-response-one",
                    "--variant",
                    "baseline",
                    "--workspace-root",
                    str(self.workspace_root),
                ]
            )

        self.assertEqual(result, 0)
        exec_commands = [command for command, _prompt, _cwd, _timeout in self.commands if "exec" in command]
        self.assertEqual(len(exec_commands), 1)
        raw = self.runner.common.EVAL_ROOT / "response/runs/run-after-skip/raw"
        self.assertEqual((raw / "case-response-one-baseline-exit.txt").read_text(encoding="utf-8"), "7\n")

    def test_unsafe_run_ids_are_rejected(self) -> None:
        self.write_case()
        for run_id in ("../escape", "nested/run", "/tmp/escape"):
            with self.subTest(run_id=run_id):
                with self.assertRaisesRegex(SystemExit, "unsafe run id"):
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
