#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("validate_eval_protocol.py")


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_eval_protocol", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ValidateEvalProtocolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = load_validator()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.run_dir = Path(self.tmp.name) / "run"

    def write_required_artifacts(self, case_id: str = "case-response-one") -> Path:
        raw = self.run_dir / "raw"
        raw.mkdir(parents=True, exist_ok=True)
        (raw / f"{case_id}-public-prompt.md").write_text("사용자 요청입니다.\n", encoding="utf-8")
        (raw / f"{case_id}-operator-prompt.txt").write_text("operator\n", encoding="utf-8")
        (raw / f"{case_id}-with-dddjango-prompt-input.json").write_text(
            '{"messages": []}\n',
            encoding="utf-8",
        )
        (raw / f"{case_id}-with-dddjango-prompt-input.stderr.txt").write_text(
            "",
            encoding="utf-8",
        )
        for variant in ("with-dddjango",):
            (raw / f"{case_id}-{variant}.txt").write_text("answer\n", encoding="utf-8")
            (raw / f"{case_id}-{variant}-events.jsonl").write_text("", encoding="utf-8")
            (raw / f"{case_id}-{variant}.stderr.txt").write_text("", encoding="utf-8")
            (raw / f"{case_id}-{variant}-command.txt").write_text("codex exec\n", encoding="utf-8")
            (raw / f"{case_id}-{variant}-exit.txt").write_text("0\n", encoding="utf-8")
        return raw

    def test_empty_with_ddjango_prompt_input_fails(self) -> None:
        raw = self.write_required_artifacts()
        (raw / "case-response-one-with-dddjango-prompt-input.json").write_text(
            "",
            encoding="utf-8",
        )

        findings = self.validator.validate_run_completeness(
            self.run_dir,
            ["case-response-one"],
            ["with-dddjango"],
        )

        self.assertTrue(
            any("with-ddjango prompt-input artifact must contain a JSON object" in finding for finding in findings),
            findings,
        )

    def test_with_ddjango_prompt_input_allows_message_array(self) -> None:
        raw = self.write_required_artifacts()
        prompt_input = raw / "case-response-one-with-dddjango-prompt-input.json"
        prompt_input.write_text(
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

        prompt_input_error = self.validator.validate_json_prompt_input_artifact(
            prompt_input,
            "with-ddjango prompt-input artifact",
        )
        findings = self.validator.validate_run_completeness(
            self.run_dir,
            ["case-response-one"],
            ["with-ddjango"],
        )

        self.assertIsNone(prompt_input_error)
        self.assertFalse(
            any("with-ddjango prompt-input artifact must contain a JSON object" in finding for finding in findings),
            findings,
        )


if __name__ == "__main__":
    unittest.main()
