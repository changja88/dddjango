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
RUN_ID_RESPONSE = "20260517-121212-response-try01-full-current-baseline"
RUN_ID_WORKFLOW = "20260517-121212-workflow-try01-full-current-baseline"
RUN_ID_CODE = "20260517-121212-code-try01-full-current-baseline"


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
        answer_text = f"id: {case_id}\ncase_id: {case_id}\nbucket: {bucket}\nkind: {bucket}\n"
        if bucket == "code":
            answer_text += (
                "code_expected: true\n"
                "deterministic_checks: []\n"
                "allowed_paths:\n"
                "  - apps/**\n"
                "forbidden_paths: []\n"
            )
        answer.write_text(answer_text, encoding="utf-8")

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
        run_id: str = RUN_ID_RESPONSE,
        variants: tuple[str, ...] = ("baseline", "with-dddjango"),
        oracle: dict[str, object] | None = None,
        include_oracle: bool = True,
        include_run_meta: bool = True,
        baseline_text: str = "baseline answer\n",
    ) -> Path:
        self.write_case(bucket, case_id)
        run_dir = self.eval_root / bucket / "runs" / run_id
        raw = run_dir / "raw"
        raw.mkdir(parents=True, exist_ok=True)
        if include_run_meta:
            self.validator.run_identity.write_run_meta(run_dir, run_id=run_id)
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
        copied = artifact_dir / "files/apps/orders/service.py"
        copied.parent.mkdir(parents=True, exist_ok=True)
        copied.write_text("print('ok')\n", encoding="utf-8")
        (artifact_dir / "changed-files.json").write_text(
            json.dumps(manifest) + "\n",
            encoding="utf-8",
        )

    def write_code_behavior_check(
        self,
        run_dir: Path,
        case_id: str,
        variant: str,
        *,
        exit_code: str,
    ) -> None:
        checks = run_dir / "code" / case_id / variant / "behavior-checks"
        checks.mkdir(parents=True, exist_ok=True)
        (checks / "hidden-command.txt").write_text("python3 hidden.py\n", encoding="utf-8")
        (checks / "hidden-exit.txt").write_text(exit_code + "\n", encoding="utf-8")
        (checks / "hidden-stdout.txt").write_text("", encoding="utf-8")
        (checks / "hidden-stderr.txt").write_text("", encoding="utf-8")

    def write_code_deterministic_check(
        self,
        run_dir: Path,
        case_id: str,
        variant: str,
        *,
        command: str,
        exit_code: str = "0",
    ) -> None:
        checks = run_dir / "code" / case_id / variant / "checks"
        checks.mkdir(parents=True, exist_ok=True)
        (checks / "unit-tests-command.txt").write_text(command + "\n", encoding="utf-8")
        (checks / "unit-tests-exit.txt").write_text(exit_code + "\n", encoding="utf-8")
        (checks / "unit-tests-stdout.txt").write_text("", encoding="utf-8")
        (checks / "unit-tests-stderr.txt").write_text("OK\n", encoding="utf-8")

    def valid_code_manifest(self, case_id: str, variant: str) -> dict[str, object]:
        return {
            "caseId": case_id,
            "variant": variant,
            "workspace": "/tmp/workspace",
            "evidenceMode": "code-backed",
            "diffPath": f"code/{case_id}/{variant}/diff.patch",
            "noCodeProduced": False,
            "files": [
                {
                    "path": "apps/orders/service.py",
                    "status": "modified",
                    "language": "python",
                    "artifactPath": f"code/{case_id}/{variant}/files/apps/orders/service.py",
                    "lineCount": 1,
                    "byteCount": 12,
                    "binary": False,
                }
            ],
        }

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
        result_count: int = 0,
        trace_status: str = "no-trace",
        parser_version: int = 1,
    ) -> None:
        trace = {
            "caseId": case_id,
            "variant": variant,
            "parserVersion": parser_version,
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
        if parser_version >= 2:
            trace["resultEventCount"] = result_count
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
        run_dir = self.write_valid_run()

        result, output = self.run_validator(
            ["--bucket", "response", "--run-id", RUN_ID_RESPONSE, "--case", "case-response-one"]
        )

        self.assertEqual(result, 0)
        self.assertIn("PASS:", output)
        manifest = json.loads((run_dir / "RUN_VALIDATION.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["status"], "passed")
        self.assertEqual(manifest["findings"], [])

    def test_stale_baseline_prompt_input_fails(self) -> None:
        run_dir = self.write_valid_run()
        (run_dir / "raw/case-response-one-baseline-prompt-input.json").write_text(
            "{}\n",
            encoding="utf-8",
        )

        self.assertFailsWith(
            ["--bucket", "response", "--run-id", RUN_ID_RESPONSE, "--case", "case-response-one"],
            "baseline prompt-input artifact is forbidden",
        )
        manifest = json.loads((run_dir / "RUN_VALIDATION.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["status"], "failed")
        self.assertIn(
            "baseline prompt-input artifact is forbidden",
            "\n".join(manifest["findings"]),
        )

    def test_invalid_run_meta_json_fails(self) -> None:
        run_dir = self.write_valid_run()
        (run_dir / "RUN_META.json").write_text("{\n", encoding="utf-8")

        with self.assertRaisesRegex(SystemExit, "RUN_META.json is not valid JSON"):
            self.validator.main(
                ["--bucket", "response", "--run-id", RUN_ID_RESPONSE, "--case", "case-response-one"]
            )

    def test_missing_run_meta_json_fails(self) -> None:
        run_id = "20260517-143012-response-try01-full-current-baseline"
        self.write_valid_run(run_id=run_id, include_run_meta=False)

        with self.assertRaisesRegex(SystemExit, "RUN_META.json is missing"):
            self.validator.main(
                ["--bucket", "response", "--run-id", run_id, "--case", "case-response-one"]
            )

    def test_invalid_oracle_schema_fails(self) -> None:
        self.write_valid_run(oracle={"caseId": "case-response-one"})

        self.assertFailsWith(
            ["--bucket", "response", "--run-id", RUN_ID_RESPONSE, "--case", "case-response-one"],
            "invalid answer-oracle schema",
        )

    def test_expected_outcomes_reject_baseline_pass_when_not_allowed(self) -> None:
        self.write_valid_run(
            oracle={
                "caseId": "case-response-one",
                "answerOracleEvaluated": True,
                "baseline": {
                    "score": "5 / 5",
                    "verdict": "pass",
                    "evaluation_summary": "strong",
                },
                "with_dddjango": {
                    "score": "5 / 5",
                    "verdict": "pass",
                    "evaluation_summary": "also strong",
                },
                "observations": ["no delta"],
            }
        )
        answer = self.eval_root / "response/answer/case-response-one.yaml"
        answer.write_text(
            answer.read_text(encoding="utf-8")
            + """expected_outcomes:
  baseline: partial
  with_dddjango: pass
  expected_delta: positive
  baseline_pass_ok: false
""",
            encoding="utf-8",
        )

        self.assertFailsWith(
            ["--bucket", "response", "--run-id", RUN_ID_RESPONSE, "--case", "case-response-one"],
            "expected_outcomes baseline_pass_ok=false conflicts with baseline verdict pass",
        )

    def test_expected_outcomes_reject_positive_delta_without_score_improvement(self) -> None:
        self.write_valid_run(
            oracle={
                "caseId": "case-response-one",
                "answerOracleEvaluated": True,
                "baseline": {
                    "score": "5 / 5",
                    "verdict": "pass",
                    "evaluation_summary": "strong",
                },
                "with_dddjango": {
                    "score": "5 / 5",
                    "verdict": "pass",
                    "evaluation_summary": "also strong",
                },
                "observations": ["no delta"],
            }
        )
        answer = self.eval_root / "response/answer/case-response-one.yaml"
        answer.write_text(
            answer.read_text(encoding="utf-8")
            + """expected_outcomes:
  baseline: pass
  with_dddjango: pass
  expected_delta: positive
  baseline_pass_ok: true
""",
            encoding="utf-8",
        )

        self.assertFailsWith(
            ["--bucket", "response", "--run-id", RUN_ID_RESPONSE, "--case", "case-response-one"],
            "expected_delta=positive requires",
        )

    def test_expected_outcomes_reject_non_negative_delta_with_lower_score(self) -> None:
        self.write_valid_run(
            oracle={
                "caseId": "case-response-one",
                "answerOracleEvaluated": True,
                "baseline": {
                    "score": "5 / 5",
                    "verdict": "pass",
                    "evaluation_summary": "strong",
                },
                "with_dddjango": {
                    "score": "4 / 5",
                    "verdict": "pass-limited",
                    "evaluation_summary": "weaker",
                },
                "observations": ["negative delta"],
            }
        )
        answer = self.eval_root / "response/answer/case-response-one.yaml"
        answer.write_text(
            answer.read_text(encoding="utf-8")
            + """expected_outcomes:
  baseline: pass
  with_dddjango: pass-or-pass-limited
  expected_delta: non-negative
  baseline_pass_ok: true
""",
            encoding="utf-8",
        )

        self.assertFailsWith(
            ["--bucket", "response", "--run-id", RUN_ID_RESPONSE, "--case", "case-response-one"],
            "expected_delta=non-negative requires",
        )

    def test_expected_outcomes_reject_with_dddjango_non_pass_when_pass_expected(self) -> None:
        self.write_valid_run(
            oracle={
                "caseId": "case-response-one",
                "answerOracleEvaluated": True,
                "baseline": {
                    "score": "1 / 5",
                    "verdict": "fail",
                    "evaluation_summary": "weak",
                },
                "with_dddjango": {
                    "score": "3 / 5",
                    "verdict": "partial",
                    "evaluation_summary": "incomplete",
                },
                "observations": ["not complete"],
            }
        )
        answer = self.eval_root / "response/answer/case-response-one.yaml"
        answer.write_text(
            answer.read_text(encoding="utf-8")
            + """expected_outcomes:
  baseline: partial
  with_dddjango: pass
  expected_delta: positive
  baseline_pass_ok: true
""",
            encoding="utf-8",
        )

        self.assertFailsWith(
            ["--bucket", "response", "--run-id", RUN_ID_RESPONSE, "--case", "case-response-one"],
            "expected_outcomes with_dddjango=pass conflicts",
        )

    def test_missing_with_ddjango_prompt_input_fails(self) -> None:
        run_dir = self.write_valid_run()
        (run_dir / "raw/case-response-one-with-dddjango-prompt-input.json").unlink()

        self.assertFailsWith(
            ["--bucket", "response", "--run-id", RUN_ID_RESPONSE, "--case", "case-response-one"],
            "missing with-ddjango prompt-input artifact",
        )

    def test_empty_with_ddjango_prompt_input_fails(self) -> None:
        run_dir = self.write_valid_run()
        (run_dir / "raw/case-response-one-with-dddjango-prompt-input.json").write_text(
            "",
            encoding="utf-8",
        )

        self.assertFailsWith(
            ["--bucket", "response", "--run-id", RUN_ID_RESPONSE, "--case", "case-response-one"],
            "with-ddjango prompt-input artifact must contain a JSON object or array",
        )

    def test_with_ddjango_prompt_input_allows_message_array(self) -> None:
        run_dir = self.write_valid_run()
        (run_dir / "raw/case-response-one-with-dddjango-prompt-input.json").write_text(
            json.dumps(
                [
                    {
                        "type": "message",
                        "role": "user",
                        "content": [{"type": "input_text", "text": "사용자 요청입니다."}],
                    }
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        result, output = self.run_validator(
            ["--bucket", "response", "--run-id", RUN_ID_RESPONSE, "--case", "case-response-one"]
        )

        self.assertEqual(result, 0)
        self.assertIn("PASS:", output)

    def test_with_ddjango_prompt_input_private_eval_sentinel_fails(self) -> None:
        run_dir = self.write_valid_run()
        (run_dir / "raw/case-response-one-with-dddjango-prompt-input.json").write_text(
            json.dumps(
                [
                    {
                        "type": "message",
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": "__DDDJANGO_PRIVATE_EVAL_SENTINEL__",
                            }
                        ],
                    }
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        self.assertFailsWith(
            ["--bucket", "response", "--run-id", RUN_ID_RESPONSE, "--case", "case-response-one"],
            "with-ddjango prompt-input artifact contains private evaluation material",
        )

    def test_with_dddjango_prompt_input_answer_schema_field_fails(self) -> None:
        run_dir = self.write_valid_run()
        (run_dir / "raw/case-response-one-with-dddjango-prompt-input.json").write_text(
            json.dumps(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": "target_behavior:\n  required:\n    - leaked answer field\n",
                        }
                    ]
                }
            )
            + "\n",
            encoding="utf-8",
        )

        self.assertFailsWith(
            ["--bucket", "response", "--run-id", RUN_ID_RESPONSE, "--case", "case-response-one"],
            "with-ddjango prompt-input artifact contains private evaluation material",
        )

    def test_with_ddjango_prompt_input_answer_path_fails(self) -> None:
        run_dir = self.write_valid_run()
        (run_dir / "raw/case-response-one-with-dddjango-prompt-input.json").write_text(
            json.dumps(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": "workspace/develop/eval/response/answer/case-response-one.yaml",
                        }
                    ]
                }
            )
            + "\n",
            encoding="utf-8",
        )

        self.assertFailsWith(
            ["--bucket", "response", "--run-id", RUN_ID_RESPONSE, "--case", "case-response-one"],
            "with-ddjango prompt-input artifact contains private evaluation material",
        )

    def test_with_ddjango_prompt_input_answer_schema_json_key_fails(self) -> None:
        run_dir = self.write_valid_run()
        (run_dir / "raw/case-response-one-with-dddjango-prompt-input.json").write_text(
            json.dumps(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": "사용자 요청입니다.",
                            "target_behavior": {"required": ["leaked answer field"]},
                        }
                    ]
                }
            )
            + "\n",
            encoding="utf-8",
        )

        self.assertFailsWith(
            ["--bucket", "response", "--run-id", RUN_ID_RESPONSE, "--case", "case-response-one"],
            "with-ddjango prompt-input artifact contains private evaluation material",
        )

    def test_nonzero_exit_fails(self) -> None:
        run_dir = self.write_valid_run()
        (run_dir / "raw/case-response-one-baseline-exit.txt").write_text("7\n", encoding="utf-8")

        self.assertFailsWith(
            ["--bucket", "response", "--run-id", RUN_ID_RESPONSE, "--case", "case-response-one"],
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
            ["--bucket", "response", "--run-id", RUN_ID_RESPONSE, "--case", "case-response-one"],
            "baseline exit is not 0",
        )

        result, output = self.run_validator(
            [
                "--bucket",
                "response",
                "--run-id",
                RUN_ID_RESPONSE,
                "--case",
                "case-response-one",
                "--allow-skipped-exits",
            ]
        )

        self.assertEqual(result, 0)
        self.assertIn("PASS:", output)

    def test_baseline_output_allows_eval_domain_terms_from_public_task(self) -> None:
        self.write_valid_run(
            baseline_text=(
                "Check dddjango/skills, plugins/dddjango, dddjango:* markers, "
                "answer-oracle files, and workspace/develop/eval/runtime/runs paths.\n"
            )
        )

        result, output = self.run_validator(
            ["--bucket", "response", "--run-id", RUN_ID_RESPONSE, "--case", "case-response-one"]
        )

        self.assertEqual(result, 0)
        self.assertIn("PASS:", output)

    def test_baseline_hidden_repo_path_contamination_fails(self) -> None:
        self.write_valid_run(
            baseline_text=(
                f"The runtime skill was loaded from "
                f"{self.root / '.codex/plugins/cache/dddjango-local'}.\n"
            )
        )

        self.assertFailsWith(
            ["--bucket", "response", "--run-id", RUN_ID_RESPONSE, "--case", "case-response-one"],
            "baseline output contains hidden repo path",
        )

    def test_with_ddjango_output_hidden_repo_path_contamination_fails(self) -> None:
        run_dir = self.write_valid_run()
        hidden = self.root / "workspace/develop/eval/response/answer/case-response-one.yaml"
        (run_dir / "raw/case-response-one-with-dddjango.txt").write_text(
            f"평가 근거 파일: {hidden}\n",
            encoding="utf-8",
        )

        self.assertFailsWith(
            ["--bucket", "response", "--run-id", RUN_ID_RESPONSE, "--case", "case-response-one"],
            "raw/case-response-one-with-dddjango.txt: output contains forbidden local path",
        )

    def test_with_ddjango_prompt_input_hidden_repo_path_contamination_fails(self) -> None:
        run_dir = self.write_valid_run()
        hidden = self.root / "workspace/develop/eval/response/answer/case-response-one.yaml"
        (run_dir / "raw/case-response-one-with-dddjango-prompt-input.json").write_text(
            json.dumps({"messages": [{"role": "user", "content": f"read {hidden}"}]}) + "\n",
            encoding="utf-8",
        )

        self.assertFailsWith(
            ["--bucket", "response", "--run-id", RUN_ID_RESPONSE, "--case", "case-response-one"],
            "raw/case-response-one-with-dddjango-prompt-input.json: output contains forbidden local path",
        )

    def test_report_html_hidden_repo_path_contamination_fails(self) -> None:
        run_dir = self.write_valid_run()
        hidden = self.root / "workspace/develop/eval/response/answer/case-response-one.yaml"
        report = run_dir / "analysis/report.html"
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(f"<html><body>{hidden}</body></html>\n", encoding="utf-8")

        self.assertFailsWith(
            ["--bucket", "response", "--run-id", RUN_ID_RESPONSE, "--case", "case-response-one"],
            "analysis/report.html: output contains forbidden local path",
        )

    def test_report_html_generic_temporary_path_contamination_fails(self) -> None:
        run_dir = self.write_valid_run()
        report = run_dir / "analysis/report.html"
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text("<html><body>/private/tmp/dddjango-eval-workspaces/case</body></html>\n", encoding="utf-8")

        self.assertFailsWith(
            ["--bucket", "response", "--run-id", RUN_ID_RESPONSE, "--case", "case-response-one"],
            "analysis/report.html: output contains temporary workspace path",
        )

    def test_baseline_response_temporary_workspace_link_does_not_block_validation(self) -> None:
        self.write_valid_run(
            baseline_text=(
                "근거: "
                "[plugin-structure.md](/private/tmp/dddjango-eval-workspaces/run/case/"
                "baseline/dddjango/.codex-plugin/plugin.json:132)\n"
            )
        )

        result, output = self.run_validator(
            ["--bucket", "response", "--run-id", RUN_ID_RESPONSE, "--case", "case-response-one"]
        )

        self.assertEqual(result, 0)
        self.assertIn("PASS:", output)

    def test_generic_tmp_wording_is_not_temporary_path_contamination(self) -> None:
        categories = self.validator.eval_leakage_policy.scan_text_for_leakage(
            "Reject home/tmp/plugin-cache absolute paths as a category.\n"
        )

        self.assertNotIn("temporary workspace path", categories)

    def test_with_ddjango_output_private_eval_sentinel_fails_without_echoing_secret(self) -> None:
        run_dir = self.write_valid_run()
        (run_dir / "raw/case-response-one-with-dddjango.txt").write_text(
            "__DDDJANGO_PRIVATE_EVAL_SENTINEL__\n",
            encoding="utf-8",
        )

        self.assertFailsWith(
            ["--bucket", "response", "--run-id", RUN_ID_RESPONSE, "--case", "case-response-one"],
            "raw/case-response-one-with-dddjango.txt: output contains internal eval sentinel",
        )

    def test_prompt_induced_sentinel_in_with_ddjango_response_is_allowed(self) -> None:
        run_dir = self.write_valid_run()
        prompt = run_dir / "raw/case-response-one-public-prompt.md"
        prompt.write_text(
            "찾을 문자열: `__DDDJANGO_PRIVATE_EVAL_SENTINEL__`\n",
            encoding="utf-8",
        )
        (run_dir / "raw/case-response-one-with-dddjango.txt").write_text(
            "찾을 문자열: `__DDDJANGO_PRIVATE_EVAL_SENTINEL__`\n",
            encoding="utf-8",
        )

        result, output = self.run_validator(
            ["--bucket", "response", "--run-id", RUN_ID_RESPONSE, "--case", "case-response-one"]
        )

        self.assertEqual(result, 0)
        self.assertIn("PASS:", output)

    def test_prompt_induced_sentinel_in_report_is_allowed(self) -> None:
        run_dir = self.write_valid_run()
        (run_dir / "raw/case-response-one-public-prompt.md").write_text(
            "찾을 문자열: `__DDDJANGO_PRIVATE_EVAL_SENTINEL__`\n",
            encoding="utf-8",
        )
        report = run_dir / "analysis/report.html"
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(
            "<html><body>__DDDJANGO_PRIVATE_EVAL_SENTINEL__</body></html>\n",
            encoding="utf-8",
        )

        result, output = self.run_validator(
            ["--bucket", "response", "--run-id", RUN_ID_RESPONSE, "--case", "case-response-one"]
        )

        self.assertEqual(result, 0)
        self.assertIn("PASS:", output)

    def test_code_output_temporary_workspace_file_link_is_allowed(self) -> None:
        case_id = "case-code-one"
        run_dir = self.write_valid_run(
            bucket="code",
            case_id=case_id,
            run_id=RUN_ID_CODE,
            variants=("with-dddjango",),
        )
        self.write_code_capture_metadata(case_id)
        self.write_code_variant_artifacts(
            run_dir,
            case_id,
            "with-dddjango",
            self.valid_code_manifest(case_id, "with-dddjango"),
        )
        (run_dir / f"raw/{case_id}-with-dddjango.txt").write_text(
            "Updated "
            "[service.py](/private/tmp/dddjango-eval-workspaces/run/case/with-dddjango/"
            "apps/orders/service.py).\n",
            encoding="utf-8",
        )

        result, output = self.run_validator(
            [
                "--bucket",
                "code",
                "--run-id",
                RUN_ID_CODE,
                "--case",
                case_id,
                "--variant",
                "with-dddjango",
            ]
        )

        self.assertEqual(result, 0)
        self.assertIn("PASS:", output)

    def test_skip_oracle_succeeds_without_canonical_oracle(self) -> None:
        self.write_valid_run(include_oracle=False)

        result, output = self.run_validator(
            [
                "--bucket",
                "response",
                "--run-id",
                RUN_ID_RESPONSE,
                "--case",
                "case-response-one",
                "--skip-oracle",
            ]
        )

        self.assertEqual(result, 0)
        self.assertIn("PASS:", output)

    def test_with_ddjango_behavior_check_failure_fails_run_validation(self) -> None:
        case_id = "case-code-one"
        run_dir = self.write_valid_run(
            bucket="code",
            case_id=case_id,
            run_id=RUN_ID_CODE,
            variants=("with-dddjango",),
        )
        self.write_code_capture_metadata(case_id)
        answer = self.eval_root / "code/answer" / f"{case_id}.yaml"
        answer.write_text(
            f"id: {case_id}\n"
            f"case_id: {case_id}\n"
            "bucket: code\n"
            "kind: code\n"
            "code_expected: true\n"
            "deterministic_checks: []\n"
            "behavior_checks:\n"
            "  - id: hidden\n"
            "    command: python3 hidden.py\n"
            "    expected_exit: 0\n"
            "allowed_paths:\n"
            "  - apps/**\n"
            "forbidden_paths: []\n",
            encoding="utf-8",
        )
        self.write_code_variant_artifacts(
            run_dir,
            case_id,
            "with-dddjango",
            self.valid_code_manifest(case_id, "with-dddjango"),
        )
        self.write_code_behavior_check(run_dir, case_id, "with-dddjango", exit_code="1")

        self.assertFailsWith(
            ["--bucket", "code", "--run-id", RUN_ID_CODE, "--case", case_id, "--variant", "with-dddjango"],
            "case-code-one with-dddjango behavior check hidden exit must be 0: 1",
        )
        manifest = json.loads((run_dir / "RUN_VALIDATION.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["status"], "failed")

    def test_workflow_run_without_trace_marker_does_not_require_trace_artifacts(self) -> None:
        case_id = "case-workflow-one"
        self.write_valid_run(bucket="workflow", case_id=case_id, run_id=RUN_ID_WORKFLOW)

        result, output = self.run_validator(
            ["--bucket", "workflow", "--run-id", RUN_ID_WORKFLOW, "--case", case_id]
        )

        self.assertEqual(result, 0)
        self.assertIn("PASS:", output)

    def test_workflow_trace_marker_requires_variant_trace_artifacts(self) -> None:
        case_id = "case-workflow-one"
        run_dir = self.write_valid_run(bucket="workflow", case_id=case_id, run_id=RUN_ID_WORKFLOW)
        self.write_trace_marker(run_dir)

        self.assertFailsWith(
            ["--bucket", "workflow", "--run-id", RUN_ID_WORKFLOW, "--case", case_id],
            "missing workflow subagent trace artifact",
        )

    def test_workflow_trace_hard_fails_reliable_actual_claim_without_trace_events(self) -> None:
        case_id = "case-workflow-one"
        run_dir = self.write_valid_run(bucket="workflow", case_id=case_id, run_id=RUN_ID_WORKFLOW)
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
            ["--bucket", "workflow", "--run-id", RUN_ID_WORKFLOW, "--case", case_id],
            "actual subagent claim has no reliable spawn/wait trace",
        )

    def test_workflow_trace_unreliable_actual_claim_is_not_validator_hard_fail(self) -> None:
        case_id = "case-workflow-one"
        run_dir = self.write_valid_run(bucket="workflow", case_id=case_id, run_id=RUN_ID_WORKFLOW)
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
            ["--bucket", "workflow", "--run-id", RUN_ID_WORKFLOW, "--case", case_id]
        )

        self.assertEqual(result, 0)
        self.assertIn("PASS:", output)

    def test_workflow_trace_parser_v2_allows_incomplete_actual_trace_for_scoring(self) -> None:
        case_id = "case-workflow-one"
        run_dir = self.write_valid_run(bucket="workflow", case_id=case_id, run_id=RUN_ID_WORKFLOW)
        self.write_trace_marker(run_dir)
        for variant in ("baseline", "with-dddjango"):
            self.write_trace(
                run_dir,
                case_id=case_id,
                variant=variant,
                trace_capture_reliable=True,
                actual_claims=["Domain Agent가 검토 완료했습니다."],
                spawn_count=1,
                wait_count=0,
                result_count=0,
                trace_status="actual-trace-incomplete",
                parser_version=2,
            )

        result, output = self.run_validator(
            ["--bucket", "workflow", "--run-id", RUN_ID_WORKFLOW, "--case", case_id]
        )

        self.assertEqual(result, 0)
        self.assertIn("PASS:", output)

    def test_workflow_trace_parser_v2_accepts_close_or_wait_result_collection(self) -> None:
        case_id = "case-workflow-one"
        run_dir = self.write_valid_run(bucket="workflow", case_id=case_id, run_id=RUN_ID_WORKFLOW)
        self.write_trace_marker(run_dir)
        for variant in ("baseline", "with-dddjango"):
            self.write_trace(
                run_dir,
                case_id=case_id,
                variant=variant,
                trace_capture_reliable=True,
                actual_claims=["Domain Agent가 검토 완료했습니다."],
                spawn_count=1,
                wait_count=0,
                result_count=1,
                trace_status="actual-trace",
                parser_version=2,
            )

        result, output = self.run_validator(
            ["--bucket", "workflow", "--run-id", RUN_ID_WORKFLOW, "--case", case_id]
        )

        self.assertEqual(result, 0)
        self.assertIn("PASS:", output)

    def test_workflow_mode_gate_rejects_stale_passing_oracle(self) -> None:
        case_id = "case-workflow-one"
        run_dir = self.write_valid_run(bucket="workflow", case_id=case_id, run_id=RUN_ID_WORKFLOW)
        answer_path = self.eval_root / "workflow/answer" / f"{case_id}.yaml"
        answer_path.write_text(
            f"id: {case_id}\ncase_id: {case_id}\nbucket: workflow\nkind: workflow\n"
            "workflow_execution_expectation:\n"
            "  expected_mode: sequential_fallback_required\n"
            "  acceptable_modes:\n"
            "    - sequential_fallback\n"
            "  forbidden_modes:\n"
            "    - actual_subagent\n"
            "    - false_actual_claim\n"
            "  decision_rule: Use fallback.\n"
            "  responsibility_rule: Do not run actual subagents.\n"
            "  report_label: sequential fallback required\n",
            encoding="utf-8",
        )
        self.write_trace_marker(run_dir)
        self.write_trace(
            run_dir,
            case_id=case_id,
            variant="baseline",
            trace_status="fallback-stated",
        )
        self.write_trace(
            run_dir,
            case_id=case_id,
            variant="with-dddjango",
            trace_status="actual-trace",
        )

        self.assertFailsWith(
            ["--bucket", "workflow", "--run-id", RUN_ID_WORKFLOW, "--case", case_id],
            "workflow execution mode actual_subagent is forbidden by oracle",
        )

    def test_workflow_mode_gate_rejects_stale_partial_oracle(self) -> None:
        case_id = "case-workflow-one"
        run_dir = self.write_valid_run(
            bucket="workflow",
            case_id=case_id,
            run_id=RUN_ID_WORKFLOW,
            oracle={
                "caseId": case_id,
                "answerOracleEvaluated": True,
                "baseline": {
                    "score": "2 / 5",
                    "verdict": "partial",
                    "evaluation_summary": "stale partial",
                },
                "with_dddjango": {
                    "score": "3 / 5",
                    "verdict": "partial",
                    "evaluation_summary": "stale partial",
                },
                "observations": ["gate should still fail"],
            },
        )
        answer_path = self.eval_root / "workflow/answer" / f"{case_id}.yaml"
        answer_path.write_text(
            f"id: {case_id}\ncase_id: {case_id}\nbucket: workflow\nkind: workflow\n"
            "workflow_execution_expectation:\n"
            "  expected_mode: sequential_fallback_required\n"
            "  acceptable_modes:\n"
            "    - sequential_fallback\n"
            "  forbidden_modes:\n"
            "    - actual_subagent\n"
            "    - false_actual_claim\n"
            "  decision_rule: Use fallback.\n"
            "  responsibility_rule: Do not run actual subagents.\n"
            "  report_label: sequential fallback required\n",
            encoding="utf-8",
        )
        self.write_trace_marker(run_dir)
        self.write_trace(
            run_dir,
            case_id=case_id,
            variant="baseline",
            trace_status="actual-trace",
        )
        self.write_trace(
            run_dir,
            case_id=case_id,
            variant="with-dddjango",
            trace_status="actual-trace",
        )

        self.assertFailsWith(
            ["--bucket", "workflow", "--run-id", RUN_ID_WORKFLOW, "--case", case_id],
            "workflow execution mode actual_subagent is forbidden by oracle",
        )

    def test_code_manifest_missing_copied_text_file_fails(self) -> None:
        case_id = "case-code-one"
        run_dir = self.write_valid_run(bucket="code", case_id=case_id, run_id=RUN_ID_CODE)
        self.write_code_capture_metadata(case_id)
        for variant in ("baseline", "with-dddjango"):
            self.write_code_variant_artifacts(
                run_dir,
                case_id,
                variant,
                self.valid_code_manifest(case_id, variant),
            )
            (
                run_dir
                / "code"
                / case_id
                / variant
                / "files/apps/orders/service.py"
            ).unlink()

        self.assertFailsWith(
            ["--bucket", "code", "--run-id", RUN_ID_CODE, "--case", case_id],
            "missing copied source file",
        )

    def test_code_manifest_empty_object_fails(self) -> None:
        case_id = "case-code-one"
        run_dir = self.write_valid_run(bucket="code", case_id=case_id, run_id=RUN_ID_CODE)
        self.write_code_capture_metadata(case_id)
        for variant in ("baseline", "with-dddjango"):
            self.write_code_variant_artifacts(run_dir, case_id, variant, {})

        self.assertFailsWith(
            ["--bucket", "code", "--run-id", RUN_ID_CODE, "--case", case_id],
            "missing keys",
        )

    def test_code_manifest_deleted_binary_file_without_text_source_fails(self) -> None:
        case_id = "case-code-one"
        run_dir = self.write_valid_run(bucket="code", case_id=case_id, run_id=RUN_ID_CODE)
        self.write_code_capture_metadata(case_id)
        for variant in ("baseline", "with-dddjango"):
            self.write_code_variant_artifacts(
                run_dir,
                case_id,
                variant,
                {
                    "caseId": case_id,
                    "variant": variant,
                    "workspace": "/tmp/workspace",
                    "evidenceMode": "code-backed",
                    "diffPath": f"code/{case_id}/{variant}/diff.patch",
                    "noCodeProduced": False,
                    "files": [
                        {
                            "path": "apps/orders/old.bin",
                            "status": "deleted",
                            "language": "text",
                            "artifactPath": "",
                            "lineCount": 0,
                            "byteCount": 0,
                            "binary": True,
                        }
                    ],
                },
            )

        self.assertFailsWith(
            ["--bucket", "code", "--run-id", RUN_ID_CODE, "--case", case_id],
            "must include at least one copied text source file",
        )

    def test_code_generated_artifact_fails_through_run_validator(self) -> None:
        case_id = "case-code-one"
        run_dir = self.write_valid_run(bucket="code", case_id=case_id, run_id=RUN_ID_CODE)
        self.write_code_capture_metadata(case_id)
        for variant in ("baseline", "with-dddjango"):
            manifest = self.valid_code_manifest(case_id, variant)
            manifest["files"] = [
                {
                    "path": "db.sqlite3",
                    "status": "added",
                    "language": "text",
                    "artifactPath": "",
                    "lineCount": 0,
                    "byteCount": 0,
                    "binary": True,
                }
            ]
            self.write_code_variant_artifacts(run_dir, case_id, variant, manifest)

        self.assertFailsWith(
            ["--bucket", "code", "--run-id", RUN_ID_CODE, "--case", case_id],
            "generated artifact changed: db.sqlite3",
        )

    def test_code_output_claiming_pytest_requires_pytest_command_artifact(self) -> None:
        case_id = "case-code-one"
        run_dir = self.write_valid_run(bucket="code", case_id=case_id, run_id=RUN_ID_CODE)
        raw = run_dir / "raw"
        (raw / f"{case_id}-with-dddjango.txt").write_text(
            "검증: tests/ 전체 pytest 실행: 8 passed\n",
            encoding="utf-8",
        )
        self.write_code_capture_metadata(case_id)
        for variant in ("baseline", "with-dddjango"):
            self.write_code_variant_artifacts(
                run_dir,
                case_id,
                variant,
                self.valid_code_manifest(case_id, variant),
            )
            self.write_code_deterministic_check(
                run_dir,
                case_id,
                variant,
                command="python3 -m unittest",
            )

        self.assertFailsWith(
            ["--bucket", "code", "--run-id", RUN_ID_CODE, "--case", case_id],
            "output claims pytest execution without matching check command artifact",
        )

    def test_code_output_can_report_unrun_pytest_without_pytest_artifact(self) -> None:
        case_id = "case-code-one"
        run_dir = self.write_valid_run(bucket="code", case_id=case_id, run_id=RUN_ID_CODE)
        raw = run_dir / "raw"
        (raw / f"{case_id}-with-dddjango.txt").write_text(
            "검증: pytest는 실행하지 않았고 python3 -m unittest만 실행했습니다.\n",
            encoding="utf-8",
        )
        self.write_code_capture_metadata(case_id)
        for variant in ("baseline", "with-dddjango"):
            self.write_code_variant_artifacts(
                run_dir,
                case_id,
                variant,
                self.valid_code_manifest(case_id, variant),
            )
            self.write_code_deterministic_check(
                run_dir,
                case_id,
                variant,
                command="python3 -m unittest",
            )

        result, output = self.run_validator(
            ["--bucket", "code", "--run-id", RUN_ID_CODE, "--case", case_id]
        )

        self.assertEqual(result, 0)
        self.assertIn("PASS:", output)

    def test_code_output_claiming_exact_unittest_command_requires_exact_command_artifact(self) -> None:
        case_id = "case-code-one"
        run_dir = self.write_valid_run(bucket="code", case_id=case_id, run_id=RUN_ID_CODE)
        raw = run_dir / "raw"
        (raw / f"{case_id}-with-dddjango.txt").write_text(
            "검증: python3 -m unittest tests.test_payments tests.test_orders 실행 통과\n",
            encoding="utf-8",
        )
        self.write_code_capture_metadata(case_id)
        for variant in ("baseline", "with-dddjango"):
            self.write_code_variant_artifacts(
                run_dir,
                case_id,
                variant,
                self.valid_code_manifest(case_id, variant),
            )
            self.write_code_deterministic_check(
                run_dir,
                case_id,
                variant,
                command="python3 -m unittest",
            )

        self.assertFailsWith(
            ["--bucket", "code", "--run-id", RUN_ID_CODE, "--case", case_id],
            "without exact matching check command artifact",
        )

    def test_code_output_claiming_pre_implementation_failure_requires_failure_artifact(self) -> None:
        case_id = "case-code-one"
        run_dir = self.write_valid_run(bucket="code", case_id=case_id, run_id=RUN_ID_CODE)
        raw = run_dir / "raw"
        (raw / f"{case_id}-with-dddjango.txt").write_text(
            "구현 전: 새 테스트가 실패하는 것을 확인했습니다.\n",
            encoding="utf-8",
        )
        self.write_code_capture_metadata(case_id)
        for variant in ("baseline", "with-dddjango"):
            self.write_code_variant_artifacts(
                run_dir,
                case_id,
                variant,
                self.valid_code_manifest(case_id, variant),
            )
            self.write_code_deterministic_check(
                run_dir,
                case_id,
                variant,
                command="python3 -m unittest",
            )

        self.assertFailsWith(
            ["--bucket", "code", "--run-id", RUN_ID_CODE, "--case", case_id],
            "pre-implementation failing/red-green verification",
        )

    def test_code_output_claiming_pre_implementation_failure_accepts_failure_artifact(self) -> None:
        case_id = "case-code-one"
        run_dir = self.write_valid_run(bucket="code", case_id=case_id, run_id=RUN_ID_CODE)
        raw = run_dir / "raw"
        (raw / f"{case_id}-with-dddjango.txt").write_text(
            "구현 전: 새 테스트가 실패하는 것을 확인했습니다.\n",
            encoding="utf-8",
        )
        self.write_code_capture_metadata(case_id)
        for variant in ("baseline", "with-dddjango"):
            self.write_code_variant_artifacts(
                run_dir,
                case_id,
                variant,
                self.valid_code_manifest(case_id, variant),
            )
            self.write_code_deterministic_check(
                run_dir,
                case_id,
                variant,
                command="python3 -m unittest",
                exit_code="1",
            )

        result, output = self.run_validator(
            ["--bucket", "code", "--run-id", RUN_ID_CODE, "--case", case_id]
        )

        self.assertEqual(result, 0)
        self.assertIn("PASS:", output)

    def test_invalid_run_id_fails(self) -> None:
        for run_id in ("../escape", "nested/run", "/tmp/escape", "two\\parts", "", "run-one"):
            with self.subTest(run_id=run_id):
                result, output = self.run_validator(
                    ["--bucket", "response", "--run-id", run_id, "--case", "case-response-one"]
                )

                self.assertEqual(result, 1)
                self.assertIn("FAIL: Invalid run id", output)

    def test_invalid_run_id_failure_reports_fail_prefix(self) -> None:
        result, output = self.run_validator(
            ["--bucket", "response", "--run-id", "../escape", "--case", "case-response-one"]
        )

        self.assertEqual(result, 1)
        self.assertIn("FAIL: Invalid run id", output)

    def test_unknown_case_failure_reports_fail_prefix(self) -> None:
        self.write_case(bucket="response", case_id="case-response-one")

        result, output = self.run_validator(
            ["--bucket", "response", "--run-id", RUN_ID_RESPONSE, "--case", "case-response-missing"]
        )

        self.assertEqual(result, 1)
        self.assertIn("FAIL: Unknown case id(s) for response: case-response-missing", output)



if __name__ == "__main__":
    unittest.main()
