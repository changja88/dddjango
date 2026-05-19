#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("validate_eval_code_artifacts.py")
CASE_ID = "case-code-example"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_eval_code_artifacts", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ValidateEvalCodeArtifactsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = load_validator()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "repo"
        self.run_dir = self.root / "workspace/develop/eval/code/runs/20260517-121212-code-try01-targeted-case-code-example"
        self.answer_dir = self.root / "workspace/develop/eval/code/answer"
        self.metadata_path = self.root / "workspace/develop/eval/code/cases/plugin/code-capture.json"
        self.answer_dir.mkdir(parents=True)
        self.metadata_path.parent.mkdir(parents=True)
        self.metadata_path.write_text(
            json.dumps(
                {
                    "cases": {
                        CASE_ID: {
                            "captureCode": True,
                            "subjectRepo": "workspace/develop/eval/code/fixtures/shop_service",
                        }
                    }
                }
            )
            + "\n",
            encoding="utf-8",
        )
        self.write_answer()
        self.write_variant_artifacts("with-dddjango")

    def write_answer(self, *, code_expected: bool = True, checks: str | None = None) -> None:
        checks_text = checks or (
            "deterministic_checks:\n"
            "  - id: unit-tests\n"
            "    command: python3 -m unittest\n"
            "    expected_exit: 0\n"
            "    evidence: command-artifact\n"
        )
        expected_text = "true" if code_expected else "false"
        reason_text = "" if code_expected else "code_expected_reason: missing external integration contract\n"
        (self.answer_dir / f"{CASE_ID}.yaml").write_text(
            f"id: {CASE_ID}\n"
            f"case_id: {CASE_ID}\n"
            "bucket: code\n"
            "kind: code\n"
            f"code_expected: {expected_text}\n"
            f"{reason_text}"
            f"{checks_text}",
            encoding="utf-8",
        )

    def write_variant_artifacts(self, variant: str) -> None:
        base = self.run_dir / "code" / CASE_ID / variant
        files = base / "files"
        files.mkdir(parents=True, exist_ok=True)
        copied = files / "app.py"
        copied.write_text("print('ok')\n", encoding="utf-8")
        (base / "diff.patch").write_text("diff --git a/app.py b/app.py\n", encoding="utf-8")
        (base / "changed-files.json").write_text(
            json.dumps(
                {
                    "caseId": CASE_ID,
                    "variant": variant,
                    "workspace": "/tmp/workspace",
                    "evidenceMode": "code-backed",
                    "diffPath": f"code/{CASE_ID}/{variant}/diff.patch",
                    "noCodeProduced": False,
                    "files": [
                        {
                            "path": "app.py",
                            "status": "modified",
                            "language": "python",
                            "artifactPath": f"code/{CASE_ID}/{variant}/files/app.py",
                            "lineCount": 1,
                            "byteCount": len(copied.read_bytes()),
                            "binary": False,
                        }
                    ],
                }
            )
            + "\n",
            encoding="utf-8",
        )

    def write_check_artifacts(self, *, variant: str = "with-dddjango", exit_code: str = "0") -> None:
        checks = self.run_dir / "code" / CASE_ID / variant / "checks"
        checks.mkdir(parents=True, exist_ok=True)
        (checks / "unit-tests-command.txt").write_text("python3 -m unittest\n", encoding="utf-8")
        (checks / "unit-tests-exit.txt").write_text(exit_code + "\n", encoding="utf-8")
        (checks / "unit-tests-stdout.txt").write_text("OK\n", encoding="utf-8")
        (checks / "unit-tests-stderr.txt").write_text("", encoding="utf-8")

    def write_behavior_check_artifacts(
        self,
        *,
        variant: str = "with-dddjango",
        exit_code: str = "0",
    ) -> None:
        checks = self.run_dir / "code" / CASE_ID / variant / "behavior-checks"
        checks.mkdir(parents=True, exist_ok=True)
        (checks / "hidden-command.txt").write_text(
            "python3 workspace/scripts/eval_code_behavior_checks.py --case case-code-example --workspace /tmp/ws\n",
            encoding="utf-8",
        )
        (checks / "hidden-exit.txt").write_text(exit_code + "\n", encoding="utf-8")
        (checks / "hidden-stdout.txt").write_text("OK\n", encoding="utf-8")
        (checks / "hidden-stderr.txt").write_text("", encoding="utf-8")

    def write_baseline_isolation_artifact(self) -> None:
        raw = self.run_dir / "raw"
        raw.mkdir(parents=True, exist_ok=True)
        (raw / f"{CASE_ID}-baseline-isolation.json").write_text(
            json.dumps({"pass": True}) + "\n",
            encoding="utf-8",
        )

    def validator_argv(self) -> list[str]:
        return [
            "--run-dir",
            str(self.run_dir),
            "--metadata",
            str(self.metadata_path),
            "--answer-dir",
            str(self.answer_dir),
            "--case",
            CASE_ID,
            "--variant",
            "with-dddjango",
        ]

    def test_missing_deterministic_check_evidence_fails(self) -> None:
        with self.assertRaisesRegex(
            AssertionError,
            "case-code-example with-dddjango missing deterministic check evidence: unit-tests",
        ):
            self.validator.main(self.validator_argv())

    def test_deterministic_check_evidence_passes(self) -> None:
        self.write_check_artifacts()
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            result = self.validator.main(self.validator_argv())

        self.assertEqual(result, 0)
        self.assertIn("code artifact validation passed: 1 checked", stdout.getvalue())

    def test_deterministic_check_exit_mismatch_fails(self) -> None:
        self.write_check_artifacts(exit_code="1")

        with self.assertRaisesRegex(
            AssertionError,
            "case-code-example with-dddjango deterministic check unit-tests exit must be 0: 1",
        ):
            self.validator.main(self.validator_argv())

    def test_forbidden_path_in_manifest_fails(self) -> None:
        self.write_answer(
            checks="deterministic_checks: []\n"
            "allowed_paths:\n"
            "  - apps/**\n"
            "forbidden_paths:\n"
            "  - db.sqlite3\n"
        )
        self.write_variant_artifacts("with-dddjango")
        manifest_path = (
            self.run_dir
            / "code"
            / CASE_ID
            / "with-dddjango"
            / "changed-files.json"
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["files"][0]["path"] = "db.sqlite3"
        manifest_path.write_text(json.dumps(manifest) + "\n", encoding="utf-8")

        with self.assertRaisesRegex(AssertionError, "forbidden path changed: db.sqlite3"):
            self.validator.main(self.validator_argv())

    def test_path_outside_allowed_paths_writes_quality_finding(self) -> None:
        self.write_answer(
            checks="deterministic_checks: []\n"
            "allowed_paths:\n"
            "  - apps/orders/**\n"
            "forbidden_paths:\n"
            "  - workspace/develop/eval/**\n"
        )
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            result = self.validator.main(self.validator_argv())

        self.assertEqual(result, 0)
        self.assertIn("code artifact validation passed: 1 checked", stdout.getvalue())
        policy_path = (
            self.run_dir
            / "code"
            / CASE_ID
            / "with-dddjango"
            / "policy-findings.json"
        )
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        self.assertEqual(policy["caseId"], CASE_ID)
        self.assertEqual(policy["variant"], "with-dddjango")
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

    def test_generated_artifact_fails_even_without_forbidden_paths(self) -> None:
        self.write_answer(
            checks="deterministic_checks: []\n"
            "allowed_paths:\n"
            "  - apps/**\n"
            "forbidden_paths: []\n"
        )
        manifest_path = (
            self.run_dir
            / "code"
            / CASE_ID
            / "with-dddjango"
            / "changed-files.json"
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["files"][0]["path"] = "db.sqlite3"
        manifest_path.write_text(json.dumps(manifest) + "\n", encoding="utf-8")

        with self.assertRaisesRegex(AssertionError, "generated artifact changed: db.sqlite3"):
            self.validator.main(self.validator_argv())

    def test_code_expected_false_forbids_code_changes(self) -> None:
        self.write_answer(
            code_expected=False,
            checks="deterministic_checks: []\n"
            "allowed_paths: []\n"
            "forbidden_paths:\n"
            "  - apps/**\n"
        )

        with self.assertRaisesRegex(AssertionError, "code_expected=false forbids code changes"):
            self.validator.main(self.validator_argv())

    def test_no_code_produced_requires_empty_files(self) -> None:
        self.write_answer(
            code_expected=False,
            checks="deterministic_checks: []\n"
            "allowed_paths: []\n"
            "forbidden_paths:\n"
            "  - apps/**\n"
        )
        manifest_path = (
            self.run_dir
            / "code"
            / CASE_ID
            / "with-dddjango"
            / "changed-files.json"
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["noCodeProduced"] = True
        manifest_path.write_text(json.dumps(manifest) + "\n", encoding="utf-8")

        with self.assertRaisesRegex(AssertionError, "noCodeProduced=true requires empty files"):
            self.validator.main(self.validator_argv())

    def test_missing_behavior_check_evidence_fails(self) -> None:
        self.write_answer(
            checks="deterministic_checks: []\n"
            "behavior_checks:\n"
            "  - id: hidden\n"
            "    command: python3 workspace/scripts/eval_code_behavior_checks.py --case case-code-example\n"
            "    expected_exit: 0\n"
        )

        with self.assertRaisesRegex(
            AssertionError,
            "case-code-example with-dddjango missing behavior check evidence: hidden",
        ):
            self.validator.main(self.validator_argv())

    def test_behavior_check_evidence_passes(self) -> None:
        self.write_answer(
            checks="deterministic_checks: []\n"
            "behavior_checks:\n"
            "  - id: hidden\n"
            "    command: python3 workspace/scripts/eval_code_behavior_checks.py --case case-code-example\n"
            "    expected_exit: 0\n"
        )
        self.write_behavior_check_artifacts()

        stdout = io.StringIO()

        with redirect_stdout(stdout):
            result = self.validator.main(self.validator_argv())

        self.assertEqual(result, 0)
        self.assertIn("code artifact validation passed: 1 checked", stdout.getvalue())

    def test_behavior_check_exit_mismatch_fails_for_with_dddjango(self) -> None:
        self.write_answer(
            checks="deterministic_checks: []\n"
            "behavior_checks:\n"
            "  - id: hidden\n"
            "    command: python3 workspace/scripts/eval_code_behavior_checks.py --case case-code-example\n"
            "    expected_exit: 0\n"
        )
        self.write_behavior_check_artifacts(exit_code="1")

        with self.assertRaisesRegex(
            AssertionError,
            "case-code-example with-dddjango behavior check hidden exit must be 0: 1",
        ):
            self.validator.main(self.validator_argv())

        policy_path = (
            self.run_dir
            / "code"
            / CASE_ID
            / "with-dddjango"
            / "policy-findings.json"
        )
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        self.assertEqual(
            policy["findings"],
            [
                {
                    "severity": "quality",
                    "rule": "behavior_check_exit",
                    "checkId": "hidden",
                    "expectedExit": "0",
                    "actualExit": "1",
                    "message": "behavior check hidden exit was 1, expected 0",
                }
            ],
        )

    def test_behavior_check_exit_mismatch_is_quality_finding_for_baseline(self) -> None:
        self.write_answer(
            checks="deterministic_checks: []\n"
            "behavior_checks:\n"
            "  - id: hidden\n"
            "    command: python3 workspace/scripts/eval_code_behavior_checks.py --case case-code-example\n"
            "    expected_exit: 0\n"
        )
        self.write_variant_artifacts("baseline")
        self.write_baseline_isolation_artifact()
        self.write_behavior_check_artifacts(variant="baseline", exit_code="1")
        stdout = io.StringIO()

        argv = self.validator_argv()
        argv[-1] = "baseline"
        with redirect_stdout(stdout):
            result = self.validator.main(argv)

        self.assertEqual(result, 0)
        self.assertIn("code artifact validation passed: 1 checked", stdout.getvalue())
        policy_path = (
            self.run_dir
            / "code"
            / CASE_ID
            / "baseline"
            / "policy-findings.json"
        )
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        self.assertEqual(policy["findings"][0]["rule"], "behavior_check_exit")


if __name__ == "__main__":
    unittest.main()
