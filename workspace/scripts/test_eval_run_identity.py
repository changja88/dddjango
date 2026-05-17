#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


MODULE_PATH = Path(__file__).with_name("eval_run_identity.py")


def load_module():
    spec = importlib.util.spec_from_file_location("eval_run_identity", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class EvalRunIdentityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_build_run_id_expected_format(self) -> None:
        stamp = datetime(2026, 5, 17, 14, 30, 12, tzinfo=ZoneInfo("Asia/Seoul"))

        run_id = self.module.build_run_id(
            bucket="runtime",
            try_number=1,
            scope="full",
            topic="current-baseline",
            created_at=stamp,
        )

        self.assertEqual(
            run_id,
            "20260517-143012-runtime-try01-full-current-baseline",
        )

    def test_parse_run_id_expected_fields(self) -> None:
        run_id = "20260517-143012-runtime-try01-full-current-baseline"

        identity = self.module.parse_run_id(run_id)

        self.assertEqual(identity.bucket, "runtime")
        self.assertEqual(identity.try_number, 1)
        self.assertEqual(identity.scope, "full")
        self.assertEqual(identity.topic, "current-baseline")
        self.assertEqual(identity.created_at, "2026-05-17T14:30:12+09:00")

    def test_parse_run_id_rejects_invalid(self) -> None:
        invalid = [
            "",
            "../escape",
            "nested/run",
            "/tmp/escape",
            "20260517-runtime-try1-full-current-baseline",
            "20260517-143012-runtime-try1-full-current-baseline",
            "20260517-143012-runtime-try01-smoke-current-baseline",
            "20260517-143012-runtime-try01-full-Current",
        ]

        for value in invalid:
            with self.subTest(value=value):
                with self.assertRaises(SystemExit):
                    self.module.parse_run_id(value)

    def test_parse_run_id_rejects_impossible_timestamp_with_system_exit(self) -> None:
        run_id = "20261340-250000-runtime-try01-full-current-baseline"

        with self.assertRaises(SystemExit):
            self.module.parse_run_id(run_id)

    def test_validate_try_number_rejects_bool(self) -> None:
        stamp = datetime(2026, 5, 17, 14, 30, 12, tzinfo=ZoneInfo("Asia/Seoul"))

        with self.assertRaises(SystemExit):
            self.module.validate_try_number(True)

        with self.assertRaises(SystemExit):
            self.module.build_run_id(
                bucket="runtime",
                try_number=True,
                scope="full",
                topic="current-baseline",
                created_at=stamp,
            )

    def test_write_and_load_run_meta(self) -> None:
        run_id = "20260517-143012-runtime-try01-full-current-baseline"
        run_dir = self.root / run_id

        meta = self.module.write_run_meta(
            run_dir,
            run_id=run_id,
            lv_up_analysis="analysis note",
            lv_up_plan="plan note",
            fingerprint={
                "case_ids": ["case-runtime-one"],
                "variants": ["baseline", "with-dddjango"],
                "model": "gpt-5.5",
                "reasoning": "xhigh",
            },
        )
        loaded = self.module.load_run_meta(run_dir)

        self.assertEqual(meta["lv_up_analysis"], "analysis note")
        self.assertEqual(meta["lv_up_plan"], "plan note")
        self.assertEqual(meta["schema_version"], 2)
        self.assertEqual(meta["fingerprint"]["case_ids"], ["case-runtime-one"])
        self.assertEqual(loaded, meta)

    def test_validate_run_meta_bucket_mismatch(self) -> None:
        run_id = "20260517-143012-runtime-try01-full-current-baseline"
        run_dir = self.root / run_id
        self.module.write_run_meta(run_dir, run_id=run_id)
        meta_path = run_dir / "RUN_META.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["bucket"] = "response"
        meta_path.write_text(json.dumps(meta, ensure_ascii=True) + "\n", encoding="utf-8")

        errors = self.module.validate_run_meta(run_dir)

        self.assertEqual(
            errors,
            ["RUN_META.json bucket must match run id bucket: runtime"],
        )

    def test_validate_run_meta_identity_mismatches(self) -> None:
        run_id = "20260517-143012-runtime-try01-full-current-baseline"
        cases = [
            (
                "scope",
                "adjacent",
                "RUN_META.json scope must match run id scope: full",
            ),
            (
                "topic",
                "other-topic",
                "RUN_META.json topic must match run id topic: current-baseline",
            ),
            (
                "try_number",
                2,
                "RUN_META.json try_number must match run id try_number: 1",
            ),
            (
                "created_at",
                "2026-05-17T14:30:13+09:00",
                "RUN_META.json created_at must match run id created_at: 2026-05-17T14:30:12+09:00",
            ),
            (
                "run_id",
                "20260517-143012-runtime-try02-full-current-baseline",
                "RUN_META.json run_id must match directory run id: 20260517-143012-runtime-try01-full-current-baseline",
            ),
            (
                "schema_version",
                1,
                "RUN_META.json schema_version must be 2",
            ),
            (
                "stamp",
                "20260517-143013",
                "RUN_META.json stamp must match run id stamp: 20260517-143012",
            ),
        ]
        for key, value, expected_error in cases:
            with self.subTest(key=key):
                run_dir = self.root / run_id
                self.module.write_run_meta(run_dir, run_id=run_id)
                meta_path = run_dir / "RUN_META.json"
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                meta[key] = value
                meta_path.write_text(json.dumps(meta, ensure_ascii=True) + "\n", encoding="utf-8")
                errors = self.module.validate_run_meta(run_dir)
                self.assertEqual(errors, [expected_error])

    def test_validate_run_meta_requires_fingerprint_object(self) -> None:
        run_id = "20260517-143012-runtime-try01-full-current-baseline"
        run_dir = self.root / run_id
        self.module.write_run_meta(run_dir, run_id=run_id)
        meta_path = run_dir / "RUN_META.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["fingerprint"] = "not-an-object"
        meta_path.write_text(json.dumps(meta, ensure_ascii=True) + "\n", encoding="utf-8")

        errors = self.module.validate_run_meta(run_dir)

        self.assertEqual(errors, ["RUN_META.json fingerprint must be an object"])

    def test_validation_manifest_marks_successful_validated_run(self) -> None:
        run_id = "20260517-143012-runtime-try01-full-current-baseline"
        run_dir = self.root / run_id
        self.module.write_run_meta(run_dir, run_id=run_id)

        self.assertFalse(self.module.has_successful_validation(run_dir))

        manifest = self.module.write_validation_manifest(
            run_dir,
            run_id=run_id,
            bucket="runtime",
            case_ids=["case-runtime-one"],
            variants=["baseline", "with-dddjango"],
            report_path=run_dir / "analysis/report.html",
            checks=[
                {
                    "name": "validate_eval_run",
                    "status": "passed",
                    "command": "workspace/scripts/validate_eval_run.py --bucket runtime",
                }
            ],
        )

        self.assertEqual(manifest["status"], "passed")
        self.assertTrue(self.module.has_successful_validation(run_dir))

    def test_validation_manifest_rejects_bucket_mismatch(self) -> None:
        run_id = "20260517-143012-runtime-try01-full-current-baseline"
        run_dir = self.root / run_id
        self.module.write_run_meta(run_dir, run_id=run_id)
        self.module.write_validation_manifest(
            run_dir,
            run_id=run_id,
            bucket="response",
            case_ids=["case-runtime-one"],
            variants=["baseline", "with-dddjango"],
            report_path=run_dir / "analysis/report.html",
            checks=[
                {
                    "name": "validate_eval_run",
                    "status": "passed",
                    "command": "workspace/scripts/validate_eval_run.py --bucket response",
                }
            ],
        )

        errors = self.module.validate_validation_manifest(run_dir)

        self.assertEqual(
            errors,
            ["VALIDATION.json bucket must match run id bucket: runtime"],
        )

    def test_validate_run_meta_lv_up_types(self) -> None:
        run_id = "20260517-143012-runtime-try01-full-current-baseline"
        for key in ("lv_up_analysis", "lv_up_plan"):
            with self.subTest(key=key):
                run_dir = self.root / run_id
                self.module.write_run_meta(run_dir, run_id=run_id)
                meta_path = run_dir / "RUN_META.json"
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                meta[key] = []
                meta_path.write_text(json.dumps(meta, ensure_ascii=True) + "\n", encoding="utf-8")
                errors = self.module.validate_run_meta(run_dir)
                self.assertEqual(
                    errors,
                    [f"RUN_META.json {key} must be a string"],
                )

    def test_validate_run_meta_non_dict_payload(self) -> None:
        run_id = "20260517-143012-runtime-try01-full-current-baseline"
        run_dir = self.root / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "RUN_META.json").write_text('["not-a-dict"]\n', encoding="utf-8")

        errors = self.module.validate_run_meta(run_dir)

        self.assertEqual(errors, ["RUN_META.json must be a JSON object"])

    def test_validate_run_meta_malformed_json_is_normalized(self) -> None:
        run_id = "20260517-143012-runtime-try01-full-current-baseline"
        run_dir = self.root / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "RUN_META.json").write_text("{bad json\n", encoding="utf-8")

        errors = self.module.validate_run_meta(run_dir)

        self.assertEqual(len(errors), 1)
        self.assertIn("RUN_META.json is not valid JSON:", errors[0])

    def test_validate_run_meta_invalid_run_dir_name(self) -> None:
        run_dir = self.root / "run-one"
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "RUN_META.json").write_text("{}", encoding="utf-8")

        errors = self.module.validate_run_meta(run_dir)

        self.assertEqual(errors, ["Invalid run id: run-one"])

    def test_has_answer_oracle_evaluation_detects_raw_artifact(self) -> None:
        run_dir = self.root / "run-one"
        raw_dir = run_dir / "raw"
        raw_dir.mkdir(parents=True)
        (run_dir / "RUN_META.json").write_text(
            json.dumps({"answerOracleEvaluated": False}) + "\n",
            encoding="utf-8",
        )

        self.assertFalse(self.module.has_answer_oracle_evaluation(run_dir))

        (raw_dir / "case-one-answer-oracle-evaluation.json").write_text(
            "{}\n",
            encoding="utf-8",
        )

        self.assertTrue(self.module.has_answer_oracle_evaluation(run_dir))

    def test_exit_artifacts_are_clean_returns_false_with_no_exit_files(self) -> None:
        run_dir = self.root / "run-one"
        (run_dir / "raw").mkdir(parents=True)

        self.assertFalse(self.module.exit_artifacts_are_clean(run_dir))

    def test_exit_artifacts_are_clean_returns_true_when_all_exit_files_are_zero(self) -> None:
        run_dir = self.root / "run-one"
        raw_dir = run_dir / "raw"
        raw_dir.mkdir(parents=True)
        (raw_dir / "case-one-exit.txt").write_text("0", encoding="utf-8")
        (raw_dir / "case-two-exit.txt").write_text("0\n", encoding="utf-8")

        self.assertTrue(self.module.exit_artifacts_are_clean(run_dir))

    def test_exit_artifacts_are_clean_returns_false_when_any_exit_file_is_nonzero(self) -> None:
        run_dir = self.root / "run-one"
        raw_dir = run_dir / "raw"
        raw_dir.mkdir(parents=True)
        (raw_dir / "case-one-exit.txt").write_text("0", encoding="utf-8")
        (raw_dir / "case-two-exit.txt").write_text("1", encoding="utf-8")

        self.assertFalse(self.module.exit_artifacts_are_clean(run_dir))

    def test_exit_artifacts_are_clean_ignores_evaluator_exit_artifacts(self) -> None:
        run_dir = self.root / "run-one"
        raw_dir = run_dir / "raw"
        raw_dir.mkdir(parents=True)
        (raw_dir / "case-one-answer-oracle-evaluation-exit.txt").write_text(
            "0\n",
            encoding="utf-8",
        )

        self.assertFalse(self.module.exit_artifacts_are_clean(run_dir))


if __name__ == "__main__":
    unittest.main()
