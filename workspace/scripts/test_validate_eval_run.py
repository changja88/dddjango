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

    def write_code_capture_metadata(self, case_id: str) -> None:
        metadata = self.validator.CODE_CAPTURE_METADATA
        metadata.parent.mkdir(parents=True, exist_ok=True)
        metadata.write_text(
            json.dumps({"cases": {case_id: {"captureCode": True}}}) + "\n",
            encoding="utf-8",
        )

    def write_code_variant_artifacts(
        self,
        run_dir: Path,
        case_id: str,
        variant: str,
        manifest: dict[str, object],
    ) -> None:
        artifact_dir = run_dir / "code" / case_id / variant
        artifact_dir.mkdir(parents=True, exist_ok=True)
        (artifact_dir / "diff.patch").write_text("diff --git a/app.py b/app.py\n", encoding="utf-8")
        (artifact_dir / "changed-files.json").write_text(
            json.dumps(manifest) + "\n",
            encoding="utf-8",
        )

    def write_trace_marker(self, run_dir: Path) -> None:
        (run_dir / "SUBAGENT_TRACE_CAPTURE.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "bucket": "workflow",
                    "createdBy": "run_eval_bucket.py",
                    "tracePolicy": "response-text-claims-plus-structured-events-when-available",
                    "stderrUsedForClaims": False,
                }
            )
            + "\n",
            encoding="utf-8",
        )

    def write_trace(
        self,
        run_dir: Path,
        *,
        case_id: str = "case-workflow-one",
        variant: str = "with-dddjango",
        trace_capture_reliable: bool = False,
        actual_claims: list[str] | None = None,
        spawn_count: int = 0,
        wait_count: int = 0,
        trace_status: str = "no-trace",
    ) -> None:
        trace = {
            "caseId": case_id,
            "variant": variant,
            "parserVersion": 1,
            "sourceKind": "structured-events" if trace_capture_reliable else "stdout-transcript",
            "traceCaptureReliable": trace_capture_reliable,
            "responseSource": f"raw/{case_id}-{variant}.txt",
            "eventSource": f"raw/{case_id}-{variant}-events.jsonl",
            "spawnEventCount": spawn_count,
            "waitEventCount": wait_count,
            "subagentToolEvents": [],
            "explicitActualClaims": actual_claims or [],
            "explicitFallbackClaims": [],
            "rolesMentioned": [],
            "traceStatus": trace_status,
        }
        path = run_dir / "raw" / f"{case_id}-{variant}-subagent-trace.json"
        path.write_text(json.dumps(trace) + "\n", encoding="utf-8")

    def run_validator(self, argv: list[str]) -> tuple[int | None, str]:
        stdout = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout):
                result = self.validator.main(argv)
        except SystemExit as exc:
            if isinstance(exc.code, int):
                return exc.code, stdout.getvalue()
            return None, stdout.getvalue()
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

    def test_skipped_exits_fail_by_default_but_pass_when_allowed(self) -> None:
        run_dir = self.write_valid_run()
        for variant in ("baseline", "with-dddjango"):
            (run_dir / f"raw/case-response-one-{variant}-exit.txt").write_text(
                "skipped\n",
                encoding="utf-8",
            )

        self.assertFailsWith(
            ["--bucket", "response", "--run-id", "run-one", "--case", "case-response-one"],
            "baseline exit is not 0",
        )

        result, output = self.run_validator(
            [
                "--bucket",
                "response",
                "--run-id",
                "run-one",
                "--case",
                "case-response-one",
                "--allow-skipped-exits",
            ]
        )

        self.assertEqual(result, 0)
        self.assertIn("PASS:", output)

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

    def test_workflow_run_without_trace_marker_does_not_require_trace_artifacts(self) -> None:
        case_id = "case-workflow-one"
        self.write_valid_run(bucket="workflow", case_id=case_id, run_id="run-workflow")

        result, output = self.run_validator(
            ["--bucket", "workflow", "--run-id", "run-workflow", "--case", case_id]
        )

        self.assertEqual(result, 0)
        self.assertIn("PASS:", output)

    def test_workflow_trace_marker_requires_variant_trace_artifacts(self) -> None:
        case_id = "case-workflow-one"
        run_dir = self.write_valid_run(bucket="workflow", case_id=case_id, run_id="run-workflow")
        self.write_trace_marker(run_dir)

        self.assertFailsWith(
            ["--bucket", "workflow", "--run-id", "run-workflow", "--case", case_id],
            "missing workflow subagent trace artifact",
        )

    def test_workflow_trace_hard_fails_reliable_actual_claim_without_trace_events(self) -> None:
        case_id = "case-workflow-one"
        run_dir = self.write_valid_run(bucket="workflow", case_id=case_id, run_id="run-workflow")
        self.write_trace_marker(run_dir)
        for variant in ("baseline", "with-dddjango"):
            self.write_trace(
                run_dir,
                case_id=case_id,
                variant=variant,
                trace_capture_reliable=True,
                actual_claims=["Domain Agent가 검토 완료했습니다."],
                trace_status="claim-without-reliable-trace",
            )

        self.assertFailsWith(
            ["--bucket", "workflow", "--run-id", "run-workflow", "--case", case_id],
            "actual subagent claim has no reliable spawn/wait trace",
        )

    def test_workflow_trace_unreliable_actual_claim_is_not_validator_hard_fail(self) -> None:
        case_id = "case-workflow-one"
        run_dir = self.write_valid_run(bucket="workflow", case_id=case_id, run_id="run-workflow")
        self.write_trace_marker(run_dir)
        for variant in ("baseline", "with-dddjango"):
            self.write_trace(
                run_dir,
                case_id=case_id,
                variant=variant,
                trace_capture_reliable=False,
                actual_claims=["Domain Agent가 검토 완료했습니다."],
                trace_status="claim-without-reliable-trace",
            )

        result, output = self.run_validator(
            ["--bucket", "workflow", "--run-id", "run-workflow", "--case", case_id]
        )

        self.assertEqual(result, 0)
        self.assertIn("PASS:", output)

    def test_code_manifest_missing_copied_text_file_fails(self) -> None:
        case_id = "case-code-one"
        run_dir = self.write_valid_run(bucket="code", case_id=case_id, run_id="run-code")
        self.write_code_capture_metadata(case_id)
        for variant in ("baseline", "with-dddjango"):
            self.write_code_variant_artifacts(
                run_dir,
                case_id,
                variant,
                {
                    "caseId": case_id,
                    "variant": variant,
                    "evidenceMode": "code-backed",
                    "diffPath": f"code/{case_id}/{variant}/diff.patch",
                    "noCodeProduced": False,
                    "files": [
                        {
                            "path": "app.py",
                            "status": "modified",
                            "artifactPath": f"code/{case_id}/{variant}/files/app.py",
                            "binary": False,
                        }
                    ],
                },
            )

        self.assertFailsWith(
            ["--bucket", "code", "--run-id", "run-code", "--case", case_id],
            "missing copied source file",
        )

    def test_code_manifest_empty_object_fails(self) -> None:
        case_id = "case-code-one"
        run_dir = self.write_valid_run(bucket="code", case_id=case_id, run_id="run-code")
        self.write_code_capture_metadata(case_id)
        for variant in ("baseline", "with-dddjango"):
            self.write_code_variant_artifacts(run_dir, case_id, variant, {})

        self.assertFailsWith(
            ["--bucket", "code", "--run-id", "run-code", "--case", case_id],
            "missing keys",
        )

    def test_code_manifest_deleted_binary_file_without_artifact_passes(self) -> None:
        case_id = "case-code-one"
        run_dir = self.write_valid_run(bucket="code", case_id=case_id, run_id="run-code")
        self.write_code_capture_metadata(case_id)
        for variant in ("baseline", "with-dddjango"):
            self.write_code_variant_artifacts(
                run_dir,
                case_id,
                variant,
                {
                    "caseId": case_id,
                    "variant": variant,
                    "evidenceMode": "code-backed",
                    "diffPath": f"code/{case_id}/{variant}/diff.patch",
                    "noCodeProduced": False,
                    "files": [
                        {
                            "path": "old.bin",
                            "status": "deleted",
                            "artifactPath": "",
                            "binary": True,
                        }
                    ],
                },
            )

        result, output = self.run_validator(
            ["--bucket", "code", "--run-id", "run-code", "--case", case_id]
        )

        self.assertEqual(result, 0)
        self.assertIn("PASS:", output)

    def test_unsafe_run_id_fails(self) -> None:
        for run_id in ("../escape", "nested/run", "/tmp/escape", "two\\parts", ""):
            with self.subTest(run_id=run_id):
                result, output = self.run_validator(
                    ["--bucket", "response", "--run-id", run_id, "--case", "case-response-one"]
                )

                self.assertEqual(result, 1)
                self.assertIn("FAIL: unsafe run id", output)

    def test_unsafe_run_id_failure_reports_fail_prefix(self) -> None:
        result, output = self.run_validator(
            ["--bucket", "response", "--run-id", "../escape", "--case", "case-response-one"]
        )

        self.assertEqual(result, 1)
        self.assertIn("FAIL: unsafe run id", output)

    def test_unknown_case_failure_reports_fail_prefix(self) -> None:
        self.write_case(bucket="response", case_id="case-response-one")

        result, output = self.run_validator(
            ["--bucket", "response", "--run-id", "run-one", "--case", "case-response-missing"]
        )

        self.assertEqual(result, 1)
        self.assertIn("FAIL: Unknown case id(s) for response: case-response-missing", output)



if __name__ == "__main__":
    unittest.main()
