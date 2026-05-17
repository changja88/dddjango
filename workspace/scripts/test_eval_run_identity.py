#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
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
            stamp=stamp,
            bucket="runtime",
            try_number=1,
            scope="full",
            topic="current-baseline",
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

    def test_write_and_load_run_meta(self) -> None:
        run_id = "20260517-143012-runtime-try01-full-current-baseline"
        meta = self.module.build_run_meta(run_id)
        run_dir = self.root / run_id

        meta_path = self.module.write_run_meta(run_dir, meta)
        loaded = self.module.load_run_meta(run_dir)

        self.assertEqual(meta_path.name, "RUN_META.json")
        self.assertEqual(loaded, meta)

    def test_validate_run_meta_bucket_mismatch(self) -> None:
        run_id = "20260517-143012-runtime-try01-full-current-baseline"
        meta = self.module.build_run_meta(run_id)
        meta["bucket"] = "response"

        error = self.module.validate_run_meta(run_id, meta)

        self.assertEqual(
            error,
            "RUN_META.json bucket must match run id bucket: runtime",
        )


if __name__ == "__main__":
    unittest.main()
