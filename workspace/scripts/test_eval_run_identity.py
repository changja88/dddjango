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
        )
        loaded = self.module.load_run_meta(run_dir)

        self.assertEqual(meta["lv_up_analysis"], "analysis note")
        self.assertEqual(meta["lv_up_plan"], "plan note")
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
                2,
                "RUN_META.json schema_version must be 1",
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

        self.assertEqual(
            errors,
            ["RUN_META.json is not valid JSON: Expecting property name enclosed in double quotes"],
        )

    def test_validate_run_meta_invalid_run_dir_name(self) -> None:
        run_dir = self.root / "run-one"
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "RUN_META.json").write_text("{}", encoding="utf-8")

        errors = self.module.validate_run_meta(run_dir)

        self.assertEqual(errors, ["Invalid run id: run-one"])


if __name__ == "__main__":
    unittest.main()
