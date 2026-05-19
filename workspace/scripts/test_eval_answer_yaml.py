#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("eval_answer_yaml.py")


def load_parser():
    spec = importlib.util.spec_from_file_location("eval_answer_yaml", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class EvalAnswerYamlTests(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = load_parser()

    def test_scalar_value_reads_unquoted_and_quoted_values(self) -> None:
        text = "case_role: ddd_direct\nkind: 'code'\n"

        self.assertEqual(self.parser.scalar_value(text, "case_role"), "ddd_direct")
        self.assertEqual(self.parser.scalar_value(text, "kind"), "code")
        self.assertIsNone(self.parser.scalar_value(text, "missing"))

    def test_list_values_reads_block_and_inline_empty_lists(self) -> None:
        text = (
            "allowed_paths:\n"
            "  - apps/orders/**\n"
            "  - tests/**\n"
            "forbidden_paths: []\n"
        )

        self.assertEqual(
            self.parser.list_values(text, "allowed_paths"),
            ["apps/orders/**", "tests/**"],
        )
        self.assertEqual(self.parser.list_values(text, "forbidden_paths"), [])

    def test_list_of_maps_reads_reference_basis_items(self) -> None:
        text = (
            "reference_basis:\n"
            "  - path: workspace/docs/ddd-implementation-standard.md\n"
            "    basis: DDD implementation order\n"
            "  - path: workspace/reference/architecture-ddd/reference/final.md\n"
            "    basis: aggregate and invariant reference\n"
        )

        self.assertEqual(
            self.parser.list_of_maps(text, "reference_basis"),
            [
                {
                    "path": "workspace/docs/ddd-implementation-standard.md",
                    "basis": "DDD implementation order",
                },
                {
                    "path": "workspace/reference/architecture-ddd/reference/final.md",
                    "basis": "aggregate and invariant reference",
                },
            ],
        )

    def test_nested_keys_reads_mapping_and_list_fields(self) -> None:
        text = (
            "ddd_observations:\n"
            "  aggregate_root: Order\n"
            "  invariants:\n"
            "    - An order cannot be placed without items.\n"
            "  test_evidence:\n"
            "    - unit test covers empty order\n"
        )

        self.assertEqual(
            self.parser.nested_keys(text, "ddd_observations"),
            {"aggregate_root", "invariants", "test_evidence"},
        )


if __name__ == "__main__":
    unittest.main()
