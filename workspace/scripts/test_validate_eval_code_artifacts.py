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

    def write_answer(self, *, checks: str | None = None) -> None:
        checks_text = checks or (
            "deterministic_checks:\n"
            "  - id: unit-tests\n"
            "    command: python3 -m unittest\n"
            "    expected_exit: 0\n"
            "    evidence: command-artifact\n"
        )
        (self.answer_dir / f"{CASE_ID}.yaml").write_text(
            f"id: {CASE_ID}\n"
            f"case_id: {CASE_ID}\n"
            "bucket: code\n"
            "kind: code\n"
            "code_expected: true\n"
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


if __name__ == "__main__":
    unittest.main()
