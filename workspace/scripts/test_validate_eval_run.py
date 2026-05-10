#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("validate_eval_run.py")


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_eval_run", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ValidateEvalRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = load_validator()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "repo"
        self.root.mkdir()
        self.eval_root = self.root / "workspace/develop/eval"
        self.validator.common.REPO_ROOT = self.root
        self.validator.common.EVAL_ROOT = self.eval_root
        self.validator.REPO_ROOT = self.root
        self.validator.EVAL_ROOT = self.eval_root
        self.validator.CODE_CAPTURE_METADATA = (
            self.eval_root / "code/cases/plugin/code-capture.json"
        )

    def write_case(self, bucket: str = "response", case_id: str = "case-response-one") -> None:
        public = self.eval_root / bucket / "cases/plugin/public" / f"{case_id}.md"
        answer = self.eval_root / bucket / "answer" / f"{case_id}.yaml"
        public.parent.mkdir(parents=True, exist_ok=True)
        answer.parent.mkdir(parents=True, exist_ok=True)
        public.write_text("사용자 요청입니다.\n", encoding="utf-8")
        answer.write_text(
            f"id: {case_id}\ncase_id: {case_id}\nbucket: {bucket}\nkind: {bucket}\n",
            encoding="utf-8",
        )

    def valid_oracle(self, case_id: str = "case-response-one") -> dict[str, object]:
        return {
            "caseId": case_id,
            "answerOracleEvaluated": True,
            "baseline": {
                "score": "2 / 5",
                "verdict": "fail",
                "evaluation_summary": "weak",
            },
            "with_dddjango": {
                "score": "5 / 5",
                "verdict": "pass",
                "evaluation_summary": "strong",
            },
            "observations": ["clear improvement"],
        }

    def write_valid_run(
        self,
        *,
        bucket: str = "response",
        case_id: str = "case-response-one",
        run_id: str = "run-one",
        variants: tuple[str, ...] = ("baseline", "with-dddjango"),
        oracle: dict[str, object] | None = None,
        include_oracle: bool = True,
        baseline_text: str = "baseline answer\n",
    ) -> Path:
        self.write_case(bucket, case_id)
        run_dir = self.eval_root / bucket / "runs" / run_id
        raw = run_dir / "raw"
        raw.mkdir(parents=True, exist_ok=True)
        (raw / f"{case_id}-public-prompt.md").write_text("사용자 요청입니다.\n", encoding="utf-8")
        (raw / f"{case_id}-operator-prompt.txt").write_text("operator prompt\n", encoding="utf-8")
        (raw / f"{case_id}-with-dddjango-prompt-input.json").write_text(
            '{"messages": []}\n',
            encoding="utf-8",
        )
        (raw / f"{case_id}-with-dddjango-prompt-input.stderr.txt").write_text(
            "",
            encoding="utf-8",
        )
        (raw / f"{case_id}-baseline-isolation.json").write_text(
            json.dumps(
                {
                    "caseId": case_id,
                    "variant": "baseline",
                    "evidenceMode": "baseline-isolation",
                    "commandUsesIgnoreUserConfig": True,
                    "commandUsesIgnoreRules": True,
                    "forbiddenPathsAbsent": True,
                    "runsFromOriginalRepoRoot": False,
                    "operatorPromptContainsOriginalRepoRoot": False,
                    "operatorPromptDddjangoSkillMetadataMentions": [],
                    "pass": True,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        for variant in variants:
            output = baseline_text if variant == "baseline" else "with-ddjango answer\n"
            (raw / f"{case_id}-{variant}.txt").write_text(output, encoding="utf-8")
            (raw / f"{case_id}-{variant}-events.jsonl").write_text("", encoding="utf-8")
            (raw / f"{case_id}-{variant}.stderr.txt").write_text("", encoding="utf-8")
            (raw / f"{case_id}-{variant}-command.txt").write_text("codex exec\n", encoding="utf-8")
            (raw / f"{case_id}-{variant}-exit.txt").write_text("0\n", encoding="utf-8")
        if include_oracle:
            (raw / f"{case_id}-answer-oracle-evaluation.json").write_text(
                json.dumps(oracle or self.valid_oracle(case_id)) + "\n",
                encoding="utf-8",
            )
        return run_dir

    def run_validator(self, argv: list[str]) -> tuple[int | None, str]:
        stdout = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout):
                result = self.validator.main(argv)
        except SystemExit as exc:
            return int(exc.code), stdout.getvalue()
        return result, stdout.getvalue()

    def assertFailsWith(self, argv: list[str], expected: str) -> None:
        result, output = self.run_validator(argv)
        self.assertEqual(result, 1)
        self.assertIn("FAIL: ", output)
        self.assertIn(expected, output)

    def test_valid_run_passes(self) -> None:
        self.write_valid_run()

        result, output = self.run_validator(
            ["--bucket", "response", "--run-id", "run-one", "--case", "case-response-one"]
        )

        self.assertEqual(result, 0)
        self.assertIn("PASS:", output)

    def test_stale_baseline_prompt_input_fails(self) -> None:
        run_dir = self.write_valid_run()
        (run_dir / "raw/case-response-one-baseline-prompt-input.json").write_text(
            "{}\n",
            encoding="utf-8",
        )

        self.assertFailsWith(
            ["--bucket", "response", "--run-id", "run-one", "--case", "case-response-one"],
            "baseline prompt-input artifact is forbidden",
        )

    def test_invalid_oracle_schema_fails(self) -> None:
        self.write_valid_run(oracle={"caseId": "case-response-one"})

        self.assertFailsWith(
            ["--bucket", "response", "--run-id", "run-one", "--case", "case-response-one"],
            "invalid answer-oracle schema",
        )

    def test_missing_with_ddjango_prompt_input_fails(self) -> None:
        run_dir = self.write_valid_run()
        (run_dir / "raw/case-response-one-with-dddjango-prompt-input.json").unlink()

        self.assertFailsWith(
            ["--bucket", "response", "--run-id", "run-one", "--case", "case-response-one"],
            "missing with-ddjango prompt-input artifact",
        )

    def test_nonzero_exit_fails(self) -> None:
        run_dir = self.write_valid_run()
        (run_dir / "raw/case-response-one-baseline-exit.txt").write_text("7\n", encoding="utf-8")

        self.assertFailsWith(
            ["--bucket", "response", "--run-id", "run-one", "--case", "case-response-one"],
            "baseline exit is not 0",
        )

    def test_baseline_contamination_fails(self) -> None:
        self.write_valid_run(
            baseline_text="The dddjango:implementation-django skill says to proceed.\n"
        )

        self.assertFailsWith(
            ["--bucket", "response", "--run-id", "run-one", "--case", "case-response-one"],
            "baseline output contains dddjango marker",
        )

    def test_skip_oracle_succeeds_without_canonical_oracle(self) -> None:
        self.write_valid_run(include_oracle=False)

        result, output = self.run_validator(
            [
                "--bucket",
                "response",
                "--run-id",
                "run-one",
                "--case",
                "case-response-one",
                "--skip-oracle",
            ]
        )

        self.assertEqual(result, 0)
        self.assertIn("PASS:", output)

    def test_code_manifest_missing_copied_text_file_fails(self) -> None:
        case_id = "case-code-one"
        run_dir = self.write_valid_run(bucket="code", case_id=case_id, run_id="run-code")
        metadata = self.validator.CODE_CAPTURE_METADATA
        metadata.parent.mkdir(parents=True, exist_ok=True)
        metadata.write_text(
            json.dumps({"cases": {case_id: {"captureCode": True}}}) + "\n",
            encoding="utf-8",
        )
        for variant in ("baseline", "with-ddjango"):
            artifact_dir = run_dir / "code" / case_id / variant
            artifact_dir.mkdir(parents=True, exist_ok=True)
            (artifact_dir / "diff.patch").write_text("diff --git a/app.py b/app.py\n", encoding="utf-8")
            (artifact_dir / "changed-files.json").write_text(
                json.dumps(
                    {
                        "caseId": case_id,
                        "variant": variant,
                        "files": [
                            {
                                "path": "app.py",
                                "status": "modified",
                                "artifactPath": f"code/{case_id}/{variant}/files/app.py",
                                "binary": False,
                            }
                        ],
                    }
                )
                + "\n",
                encoding="utf-8",
            )

        self.assertFailsWith(
            ["--bucket", "code", "--run-id", "run-code", "--case", case_id],
            "missing copied source file",
        )

    def test_unsafe_run_id_fails(self) -> None:
        for run_id in ("../escape", "nested/run", "/tmp/escape", "two\\parts", ""):
            with self.subTest(run_id=run_id):
                with self.assertRaisesRegex(SystemExit, "unsafe run id"):
                    self.validator.main(
                        ["--bucket", "response", "--run-id", run_id, "--case", "case-response-one"]
                    )


if __name__ == "__main__":
    unittest.main()
