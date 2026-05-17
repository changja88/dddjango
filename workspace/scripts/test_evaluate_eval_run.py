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


MODULE_PATH = Path(__file__).with_name("evaluate_eval_run.py")
RUN_ID_RESPONSE = "20260517-111111-response-try01-full-current-baseline"
RUN_ID_WORKFLOW = "20260517-111111-workflow-try01-full-current-baseline"
RUN_ID_CODE = "20260517-111111-code-try01-full-current-baseline"


def load_evaluator():
    spec = importlib.util.spec_from_file_location("evaluate_eval_run", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class EvaluateEvalRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self.evaluator = load_evaluator()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "repo"
        self.root.mkdir()
        self.evaluator.common.REPO_ROOT = self.root
        self.evaluator.common.EVAL_ROOT = self.root / "workspace/develop/eval"
        self.evaluator.REPO_ROOT = self.root
        self.evaluator.EVAL_ROOT = self.evaluator.common.EVAL_ROOT

    def write_case_and_run(
        self,
        *,
        bucket: str = "response",
        case_id: str = "case-response-one",
        run_id: str = RUN_ID_RESPONSE,
        baseline_text: str = "baseline answer\n",
        with_ddjango_text: str = "with answer\n",
        write_meta: bool = True,
    ) -> Path:
        bucket_root = self.evaluator.EVAL_ROOT / bucket
        public_path = bucket_root / "cases/plugin/public" / f"{case_id}.md"
        answer_path = bucket_root / "answer" / f"{case_id}.yaml"
        raw = bucket_root / "runs" / run_id / "raw"
        public_path.parent.mkdir(parents=True, exist_ok=True)
        answer_path.parent.mkdir(parents=True, exist_ok=True)
        raw.mkdir(parents=True, exist_ok=True)
        public_path.write_text("사용자 요청입니다.\n", encoding="utf-8")
        answer_path.write_text(
            f"id: {case_id}\ncase_id: {case_id}\nbucket: {bucket}\nkind: {bucket}\n"
            "target_behavior:\n  required:\n    - answer the request\n"
            "scoring_checks:\n  - pass if answer is grounded\n",
            encoding="utf-8",
        )
        (raw / f"{case_id}-baseline.txt").write_text(baseline_text, encoding="utf-8")
        with_variant = self.evaluator.common.VARIANTS[1]
        (raw / f"{case_id}-{with_variant}.txt").write_text(with_ddjango_text, encoding="utf-8")
        if write_meta:
            self.evaluator.run_identity.write_run_meta(raw.parent, run_id=run_id)
        return raw

    def write_trace_summary(
        self,
        raw: Path,
        *,
        case_id: str,
        variant: str,
        trace_status: str = "fallback-stated",
    ) -> None:
        (raw / f"{case_id}-{variant}-subagent-trace.json").write_text(
            json.dumps(
                {
                    "caseId": case_id,
                    "variant": variant,
                    "parserVersion": 1,
                    "sourceKind": "stdout-transcript",
                    "traceCaptureReliable": False,
                    "responseSource": f"raw/{case_id}-{variant}.txt",
                    "eventSource": f"raw/{case_id}-{variant}-events.jsonl",
                    "spawnEventCount": 0,
                    "waitEventCount": 0,
                    "subagentToolEvents": [],
                    "explicitActualClaims": [],
                    "explicitFallbackClaims": ["subagent는 사용하지 않고 순차 검토했습니다."],
                    "rolesMentioned": ["Domain Agent"],
                    "traceStatus": trace_status,
                }
            )
            + "\n",
            encoding="utf-8",
        )

    def valid_payload(self, case_id: str = "case-response-one") -> dict[str, object]:
        return {
            "caseId": case_id,
            "answerOracleEvaluated": True,
            "baseline": {
                "score": "2 / 5",
                "verdict": "fail",
                "evaluation_summary": "기준 충족이 약합니다.",
                "evaluation": "기준 충족이 약합니다.",
            },
            "with_dddjango": {
                "score": "5 / 5",
                "verdict": "pass",
                "evaluation_summary": "기준을 잘 충족합니다.",
                "evaluation": "기준을 잘 충족합니다.",
            },
            "observations": ["with-dddjango 응답이 명확히 개선되었습니다."],
            "status": "ok",
        }

    def test_evaluator_writes_canonical_oracle_json(self) -> None:
        self.write_case_and_run()
        payload = self.valid_payload()

        def fake_run(command, *, prompt, cwd, timeout_seconds):
            self.assertEqual(command[:3], ["codex", "exec", "--ephemeral"])
            self.assertIn("--ignore-user-config", command)
            self.assertIn("--ignore-rules", command)
            self.assertIn("-s", command)
            self.assertIn("read-only", command)
            self.assertIn("-m", command)
            self.assertIn("gpt-5.5", command)
            self.assertIn('model_reasoning_effort="high"', command)
            self.assertEqual(cwd, self.root)
            self.assertEqual(timeout_seconds, 1800)
            self.assertIn("EVALUATOR-ONLY ANSWER ORACLE", prompt)
            self.assertIn('"answerOracleEvaluated": true', prompt)
            self.assertIn('"evaluation_summary"', prompt)
            self.assertIn("한국어", prompt)
            self.assertIn("All human-readable", prompt)
            self.assertIn(
                "Allowed verdict values: pass, partial, pass-limited, pass-control, fail, blocked.",
                prompt,
            )
            self.assertIn("Scores must be written as 0 / 5 through 5 / 5.", prompt)
            self.assertIn("baseline answer", prompt)
            self.assertIn("with answer", prompt)
            return subprocess.CompletedProcess(command, 0, json.dumps(payload), "")

        with patch.object(self.evaluator, "run_command", side_effect=fake_run):
            result = self.evaluator.main(
                [
                    "--bucket",
                    "response",
                    "--run-id",
                    RUN_ID_RESPONSE,
                    "--case",
                    "case-response-one",
                ]
            )

        self.assertEqual(result, 0)
        raw = self.evaluator.EVAL_ROOT / f"response/runs/{RUN_ID_RESPONSE}/raw"
        output = raw / "case-response-one-answer-oracle-evaluation.json"
        value = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(value["with_dddjango"]["verdict"], "pass")
        self.assertEqual(
            (raw / "case-response-one-answer-oracle-evaluation.raw.txt").read_text(
                encoding="utf-8"
            ),
            json.dumps(payload),
        )
        command_text = (
            raw / "case-response-one-answer-oracle-evaluation-command.txt"
        ).read_text(encoding="utf-8")
        self.assertIn("codex exec --ephemeral", command_text)

    def test_main_rejects_missing_run_meta_before_evaluating(self) -> None:
        raw = self.write_case_and_run(write_meta=False)

        with patch.object(self.evaluator, "run_command", side_effect=AssertionError("evaluated")):
            with self.assertRaisesRegex(SystemExit, "RUN_META.json is missing"):
                self.evaluator.main(
                    [
                        "--bucket",
                        "response",
                        "--run-id",
                        RUN_ID_RESPONSE,
                        "--case",
                        "case-response-one",
                    ]
                )

        self.assertFalse((raw / "case-response-one-answer-oracle-evaluation.raw.txt").exists())

    def test_workflow_trace_summary_is_included_as_evaluator_evidence(self) -> None:
        case_id = "case-workflow-one"
        raw = self.write_case_and_run(
            bucket="workflow",
            case_id=case_id,
            run_id=RUN_ID_WORKFLOW,
            baseline_text="baseline workflow answer\n",
            with_ddjango_text="with workflow answer\n",
        )
        for variant in self.evaluator.common.VARIANTS:
            self.write_trace_summary(raw, case_id=case_id, variant=variant)
        payload = self.valid_payload(case_id)

        def fake_run(command, *, prompt, cwd, timeout_seconds):
            self.assertIn("Workflow subagent trace summary", prompt)
            self.assertIn(f"raw/{case_id}-baseline-subagent-trace.json", prompt)
            self.assertIn(f"raw/{case_id}-with-dddjango-subagent-trace.json", prompt)
            self.assertIn("rolesMentioned", prompt)
            self.assertIn("Do not use rolesMentioned alone as scoring proof", prompt)
            self.assertIn("If the workflow oracle includes workflow_execution_expectation", prompt)
            return subprocess.CompletedProcess(command, 0, json.dumps(payload), "")

        with patch.object(self.evaluator, "run_command", side_effect=fake_run):
            result = self.evaluator.main(
                ["--bucket", "workflow", "--run-id", RUN_ID_WORKFLOW, "--case", case_id]
            )

        self.assertEqual(result, 0)

    def test_english_only_evaluator_explanation_is_rejected(self) -> None:
        self.write_case_and_run()
        payload = self.valid_payload()
        payload["baseline"]["evaluation_summary"] = "Weak answer"
        payload["baseline"]["evaluation"] = "Weak answer"

        with patch.object(
            self.evaluator,
            "run_command",
            return_value=subprocess.CompletedProcess(["codex"], 0, json.dumps(payload), ""),
        ):
            with self.assertRaises(SystemExit) as raised:
                self.evaluator.main(
                    [
                        "--bucket",
                        "response",
                        "--run-id",
                        RUN_ID_RESPONSE,
                        "--case",
                        "case-response-one",
                    ]
                )

        self.assertIn("must include Korean", str(raised.exception))

    def test_json_embedded_in_prose_is_parsed(self) -> None:
        self.write_case_and_run()
        payload = self.valid_payload()
        stdout = "Here is the evaluation:\n" + json.dumps(payload) + "\nDone.\n"

        with patch.object(
            self.evaluator,
            "run_command",
            return_value=subprocess.CompletedProcess(["codex"], 0, stdout, ""),
        ):
            result = self.evaluator.main(
                [
                    "--bucket",
                    "response",
                    "--run-id",
                    RUN_ID_RESPONSE,
                    "--case",
                    "case-response-one",
                ]
            )

        self.assertEqual(result, 0)
        output = (
            self.evaluator.EVAL_ROOT
            / f"response/runs/{RUN_ID_RESPONSE}/raw/case-response-one-answer-oracle-evaluation.json"
        )
        self.assertEqual(json.loads(output.read_text(encoding="utf-8")), payload)

    def test_invalid_schema_exits_without_canonical_oracle(self) -> None:
        raw = self.write_case_and_run()

        def fake_run(command, *, prompt, cwd, timeout_seconds):
            return subprocess.CompletedProcess(command, 0, '{"caseId": "case-response-one"}', "err\n")

        with patch.object(self.evaluator, "run_command", side_effect=fake_run):
            with self.assertRaises(SystemExit):
                self.evaluator.main(
                    [
                        "--bucket",
                        "response",
                        "--run-id",
                        RUN_ID_RESPONSE,
                        "--case",
                        "case-response-one",
                    ]
                )

        self.assertFalse((raw / "case-response-one-answer-oracle-evaluation.json").exists())
        self.assertTrue((raw / "case-response-one-answer-oracle-evaluation.raw.txt").is_file())
        self.assertTrue((raw / "case-response-one-answer-oracle-evaluation.stderr.txt").is_file())
        self.assertTrue((raw / "case-response-one-answer-oracle-evaluation-command.txt").is_file())
        self.assertTrue((raw / "case-response-one-answer-oracle-evaluation-exit.txt").is_file())

    def test_invalid_schema_rerun_removes_previous_canonical_oracle(self) -> None:
        raw = self.write_case_and_run()
        output = raw / "case-response-one-answer-oracle-evaluation.json"
        output.write_text(json.dumps(self.valid_payload()) + "\n", encoding="utf-8")

        with patch.object(
            self.evaluator,
            "run_command",
            return_value=subprocess.CompletedProcess(["codex"], 0, '{"caseId": "case-response-one"}', ""),
        ):
            with self.assertRaises(SystemExit):
                self.evaluator.main(
                    [
                        "--bucket",
                        "response",
                        "--run-id",
                        RUN_ID_RESPONSE,
                        "--case",
                        "case-response-one",
                        "--rerun",
                    ]
                )

        self.assertFalse(output.exists())

    def test_existing_canonical_json_skips_without_rerun(self) -> None:
        raw = self.write_case_and_run()
        output = raw / "case-response-one-answer-oracle-evaluation.json"
        output.write_text(json.dumps(self.valid_payload()) + "\n", encoding="utf-8")

        with patch.object(self.evaluator, "run_command", side_effect=AssertionError("reran")):
            result = self.evaluator.main(
                [
                    "--bucket",
                    "response",
                    "--run-id",
                    RUN_ID_RESPONSE,
                    "--case",
                    "case-response-one",
                ]
            )

        self.assertEqual(result, 0)

    def test_rerun_replaces_existing_canonical_json(self) -> None:
        raw = self.write_case_and_run()
        output = raw / "case-response-one-answer-oracle-evaluation.json"
        output.write_text('{"old": true}\n', encoding="utf-8")
        payload = self.valid_payload()

        with patch.object(
            self.evaluator,
            "run_command",
            return_value=subprocess.CompletedProcess(["codex"], 0, json.dumps(payload), ""),
        ):
            result = self.evaluator.main(
                [
                    "--bucket",
                    "response",
                    "--run-id",
                    RUN_ID_RESPONSE,
                    "--case",
                    "case-response-one",
                    "--rerun",
                ]
            )

        self.assertEqual(result, 0)
        self.assertEqual(json.loads(output.read_text(encoding="utf-8")), payload)

    def test_code_artifacts_are_included_and_truncated(self) -> None:
        case_id = "case-code-one"
        run_id = RUN_ID_CODE
        self.write_case_and_run(bucket="code", case_id=case_id, run_id=run_id)
        run_dir = self.evaluator.EVAL_ROOT / "code/runs" / run_id
        long_text = "x" * (self.evaluator.MAX_ARTIFACT_CHARS + 20)
        with_variant = self.evaluator.common.VARIANTS[1]
        for variant in self.evaluator.common.VARIANTS:
            artifact_dir = run_dir / "code" / case_id / variant
            files_dir = artifact_dir / "files" / "apps" / "orders"
            artifact_dir.mkdir(parents=True, exist_ok=True)
            files_dir.mkdir(parents=True, exist_ok=True)
            (artifact_dir / "diff.patch").write_text(long_text, encoding="utf-8")
            (artifact_dir / "changed-files.json").write_text(
                json.dumps({"files": [{"path": f"{variant}.py"}]}),
                encoding="utf-8",
            )
            (files_dir / "service.py").write_text(
                f"class {variant.replace('-', '_').title().replace('_', '')}OrderService:\n"
                f"    source = {variant!r}\n",
                encoding="utf-8",
            )
        payload = self.valid_payload(case_id)

        def fake_run(command, *, prompt, cwd, timeout_seconds):
            self.assertIn(f"code/{case_id}/baseline/diff.patch", prompt)
            self.assertIn(f"code/{case_id}/{with_variant}/diff.patch", prompt)
            self.assertIn(f"code/{case_id}/baseline/files/apps/orders/service.py", prompt)
            self.assertIn(f"code/{case_id}/{with_variant}/files/apps/orders/service.py", prompt)
            self.assertIn("BaselineOrderService", prompt)
            self.assertIn("WithDddjangoOrderService", prompt)
            self.assertIn("[TRUNCATED after 80000 characters]", prompt)
            self.assertNotIn("x" * (self.evaluator.MAX_ARTIFACT_CHARS + 1), prompt)
            return subprocess.CompletedProcess(command, 0, json.dumps(payload), "")

        with patch.object(self.evaluator, "run_command", side_effect=fake_run):
            result = self.evaluator.main(
                [
                    "--bucket",
                    "code",
                    "--run-id",
                    run_id,
                    "--case",
                    case_id,
                ]
            )

        self.assertEqual(result, 0)

    def test_canonical_oracle_backfills_missing_evaluation_summary(self) -> None:
        self.write_case_and_run()
        payload = self.valid_payload()
        for variant_key in ("baseline", "with_dddjango"):
            del payload[variant_key]["evaluation_summary"]

        with patch.object(
            self.evaluator,
            "run_command",
            return_value=subprocess.CompletedProcess(["codex"], 0, json.dumps(payload), ""),
        ):
            result = self.evaluator.main(
                [
                    "--bucket",
                    "response",
                    "--run-id",
                    RUN_ID_RESPONSE,
                    "--case",
                    "case-response-one",
                ]
            )

        self.assertEqual(result, 0)
        output = (
            self.evaluator.EVAL_ROOT
            / f"response/runs/{RUN_ID_RESPONSE}/raw/case-response-one-answer-oracle-evaluation.json"
        )
        value = json.loads(output.read_text(encoding="utf-8"))
        for variant_key in ("baseline", "with_dddjango"):
            self.assertEqual(
                value[variant_key]["evaluation_summary"],
                value[variant_key]["evaluation"],
            )

    def test_canonical_oracle_backfills_missing_evaluation(self) -> None:
        self.write_case_and_run()
        payload = self.valid_payload()
        for variant_key in ("baseline", "with_dddjango"):
            del payload[variant_key]["evaluation"]

        with patch.object(
            self.evaluator,
            "run_command",
            return_value=subprocess.CompletedProcess(["codex"], 0, json.dumps(payload), ""),
        ):
            result = self.evaluator.main(
                [
                    "--bucket",
                    "response",
                    "--run-id",
                    RUN_ID_RESPONSE,
                    "--case",
                    "case-response-one",
                ]
            )

        self.assertEqual(result, 0)
        output = (
            self.evaluator.EVAL_ROOT
            / f"response/runs/{RUN_ID_RESPONSE}/raw/case-response-one-answer-oracle-evaluation.json"
        )
        value = json.loads(output.read_text(encoding="utf-8"))
        for variant_key in ("baseline", "with_dddjango"):
            self.assertEqual(
                value[variant_key]["evaluation"],
                value[variant_key]["evaluation_summary"],
            )

    def test_workflow_mode_gate_overrides_evaluator_pass(self) -> None:
        case_id = "case-workflow-one"
        raw = self.write_case_and_run(
            bucket="workflow",
            case_id=case_id,
            run_id=RUN_ID_WORKFLOW,
            baseline_text="baseline workflow answer\n",
            with_ddjango_text="with workflow answer\n",
        )
        answer_path = self.evaluator.EVAL_ROOT / "workflow/answer" / f"{case_id}.yaml"
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
        self.write_trace_summary(
            raw,
            case_id=case_id,
            variant="baseline",
            trace_status="fallback-stated",
        )
        self.write_trace_summary(
            raw,
            case_id=case_id,
            variant="with-dddjango",
            trace_status="actual-trace",
        )
        payload = self.valid_payload(case_id)

        with patch.object(
            self.evaluator,
            "run_command",
            return_value=subprocess.CompletedProcess(["codex"], 0, json.dumps(payload), ""),
        ):
            result = self.evaluator.main(
                ["--bucket", "workflow", "--run-id", RUN_ID_WORKFLOW, "--case", case_id]
            )

        self.assertEqual(result, 0)
        output = raw / f"{case_id}-answer-oracle-evaluation.json"
        value = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(value["with_dddjango"]["score"], "0 / 5")
        self.assertEqual(value["with_dddjango"]["verdict"], "fail")
        self.assertIn(
            "workflow 실행 모드 hard gate",
            value["with_dddjango"]["evaluation_summary"],
        )
        self.assertTrue(
            any("actual_subagent" in observation for observation in value["observations"])
        )

    def test_unsafe_run_ids_are_rejected(self) -> None:
        self.write_case_and_run()
        for run_id in ("../escape", "nested/run", "/tmp/escape", "two\\parts", "", "run-one"):
            with self.subTest(run_id=run_id):
                with self.assertRaisesRegex(SystemExit, "Invalid run id"):
                    self.evaluator.main(
                        [
                            "--bucket",
                            "response",
                            "--run-id",
                            run_id,
                            "--case",
                            "case-response-one",
                        ]
                    )


if __name__ == "__main__":
    unittest.main()
