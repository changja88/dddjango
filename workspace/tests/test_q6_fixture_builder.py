from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import shlex
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
BUILDER = REPO_ROOT / "workspace" / "eval" / "tools" / "q6_fixture_builder.py"


class Q6FixtureBuilderTest(unittest.TestCase):
    def load_builder(self):
        spec = importlib.util.spec_from_file_location("q6_fixture_builder", BUILDER)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_builds_seven_reproducible_scenarios_without_oracle_leakage(self) -> None:
        builder = self.load_builder()
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "fixtures"
            second_output = Path(temporary_directory) / "fixtures-second"
            builder.build_all(output)
            builder.build_all(second_output)

            relative_files = sorted(
                path.relative_to(output)
                for path in output.rglob("*")
                if path.is_file()
            )
            second_relative_files = sorted(
                path.relative_to(second_output)
                for path in second_output.rglob("*")
                if path.is_file()
            )
            self.assertEqual(relative_files, second_relative_files)
            for relative in relative_files:
                self.assertEqual(
                    (output / relative).read_bytes(),
                    (second_output / relative).read_bytes(),
                )

            fixtures_root = output / "fixtures"
            control_root = output / "evaluator-control"
            staged_root = Path(temporary_directory) / "runtime-workspaces"
            fixtures = sorted(path.name for path in fixtures_root.iterdir())
            self.assertEqual(sorted(builder.SCENARIOS), fixtures)
            self.assertEqual(7, len(fixtures))
            self.assertTrue(all(re.fullmatch(r"q6-\d{2}", name) for name in fixtures))
            evaluation_manifest = json.loads(
                (control_root / "EVALUATION-MANIFEST.json").read_text()
            )
            self.assertEqual("dddjango-q6-v6", evaluation_manifest["format"])
            self.assertEqual("1.1.0", evaluation_manifest["plugin_version"])
            self.assertEqual(
                "not executed by this builder",
                evaluation_manifest["live_run_status"],
            )
            for fixture in fixtures_root.iterdir():
                control = control_root / fixture.name
                crib = json.loads((control / "CRIB.json").read_text())
                oracle = json.loads((control / "ORACLE.json").read_text())
                manifest = json.loads(
                    (control / "FIXTURE-MANIFEST.json").read_text()
                )
                self.assertTrue(crib["user_input_verbatim"])
                self.assertTrue(crib["g0_answers"])
                self.assertTrue(crib["g1_answers"])
                self.assertTrue(crib["g2_answers"])
                self.assertNotIn("scenario", crib)
                self.assertNotIn("expected_adjustments", crib)
                self.assertEqual(builder.INVENTORY_COLUMNS, oracle["inventory_columns"])
                self.assertEqual(
                    "blind grader matches required current facts; wording and row order are not graded",
                    oracle["inventory_comparison"]["rule"],
                )
                self.assertTrue(oracle["expected_inventory_obligations"])
                self.assertTrue(oracle["expected_adjustments"])
                self.assertNotIn(
                    "tests.test_unrelated_health.UnrelatedHealthTest.test_unrelated_project_health",
                    oracle["expected_adjustments"],
                )
                fixture_text = "\n".join(
                    path.read_text(encoding="utf-8")
                    for path in fixture.rglob("*")
                    if path.is_file()
                )
                self.assertNotIn("expected_adjustments", fixture_text)
                self.assertFalse((fixture / ".q6").exists())
                for relative, expected in manifest["sha256"].items():
                    actual = hashlib.sha256((fixture / relative).read_bytes()).hexdigest()
                    self.assertEqual(expected, actual)
                self.assertEqual(
                    sorted(manifest["sha256"]),
                    sorted(
                        path.relative_to(fixture).as_posix()
                        for path in fixture.rglob("*")
                        if path.is_file()
                    ),
                )
                runtime = staged_root / fixture.name
                staged_crib = builder.stage_runtime_fixture(
                    output, fixture.name, runtime
                )
                self.assertEqual(crib, staged_crib)
                self.assertFalse((runtime / "evaluator-control").exists())
                execution = subprocess.run(
                    shlex.split(staged_crib["project_runner"]),
                    cwd=runtime,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(0, execution.returncode, execution.stdout + execution.stderr)
                self.assertIn(
                    "test_unrelated_project_health",
                    execution.stdout + execution.stderr,
                )

    def test_external_migration_failure_is_deterministic_and_controlled(self) -> None:
        builder = self.load_builder()
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "q6"
            builder.build_all(output)
            control = output / "evaluator-control" / builder.CASE_EXTERNAL_MIGRATION
            crib = json.loads((control / "CRIB.json").read_text())
            oracle = json.loads((control / "ORACLE.json").read_text())
            runtime = (
                Path(temporary_directory) / "runtime" / builder.CASE_EXTERNAL_MIGRATION
            )
            staged_crib = builder.stage_runtime_fixture(
                output, builder.CASE_EXTERNAL_MIGRATION, runtime
            )
            self.assertEqual(crib, staged_crib)
            execution = subprocess.run(
                shlex.split(staged_crib["project_runner"]),
                cwd=runtime,
                env={**os.environ, **staged_crib["runtime_environment"]},
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(0, execution.returncode)
            self.assertIn(
                "simulated external-owned migration lifecycle dependency",
                execution.stdout + execution.stderr,
            )
            transcript = execution.stdout + execution.stderr
            self.assertIn("test_current_display", transcript)
            self.assertIn("test_unrelated_project_health", transcript)
            self.assertIn("test_external_migration_asset_exists", transcript)
            self.assertIn("Ran 3 tests", transcript)
            self.assertEqual(
                "blocked_external_dependency",
                oracle["expected_completion"],
            )

    def test_security_and_support_end_oracles_are_unambiguous(self) -> None:
        builder = self.load_builder()
        scenario_a = builder.SCENARIOS[builder.CASE_SUPPORT_END]
        scenario_b = builder.SCENARIOS[builder.CASE_SUPPORTED_VERSIONS]
        scenario_c = builder.SCENARIOS[builder.CASE_PERSISTED_READ]
        scenario_e = builder.SCENARIOS[builder.CASE_CHARACTERIZATION]
        scenario_f = builder.SCENARIOS[builder.CASE_EXTERNAL_MIGRATION]
        scenario_g = builder.SCENARIOS[builder.CASE_EXPLICIT_ABSENCE]

        self.assertIn("wire/state에 X가 남아 있어도 허용", scenario_a["user_input"])
        self.assertEqual(
            ["X absence/nonexistence contract"],
            scenario_a["forbidden_new_tests"],
        )
        self.assertIn(
            "email must remain masked",
            scenario_b["evidence_rows"][0]["security/privacy/regulatory"],
        )
        self.assertEqual(
            "email masked",
            scenario_b["evidence_rows"][1]["security/privacy/regulatory"],
        )
        self.assertEqual(
            "add",
            scenario_c["expected_new_test_obligations"][0]["action"],
        )
        self.assertEqual(
            "runtime-selected; exact name is not graded",
            scenario_c["expected_new_test_obligations"][0]["node_id"],
        )
        self.assertEqual(2, len(scenario_c["evidence_rows"]))
        self.assertEqual(
            "record/event-v2 write",
            scenario_c["evidence_rows"][1]["surface/version"],
        )
        self.assertEqual(
            "update",
            scenario_f["expected_adjustments"][
                "tests.test_current_display.CurrentDisplayTest.test_current_display"
            ],
        )
        self.assertEqual(
            "delete",
            scenario_e["expected_adjustments"][
                "tests.test_legacy_characterization.LegacyCharacterizationTest.test_temporary_single_iteration_detail"
            ],
        )
        self.assertEqual(
            {"Q6_EXTERNAL_MIGRATION_FAILURE": "1"},
            scenario_f["runtime_environment"],
        )
        self.assertEqual(
            [
                "tests/test_schema_history.py",
                "contract_app/migrations/0001_initial.py",
            ],
            scenario_f["expected_untouched_external_paths"],
        )
        self.assertEqual(
            scenario_f["expected_untouched_external_paths"],
            scenario_f["g0_answers"]["external_owned_opaque_paths"],
        )
        self.assertNotIn(
            "tests/test_schema_history.py",
            scenario_f["expected_adjustments"],
        )
        self.assertIn(
            "contract_app/models.py",
            scenario_f["expected_application_changes"],
        )
        self.assertEqual(
            "retain",
            scenario_g["expected_adjustments"][
                "tests.test_profile_absence.ProfileAbsenceTest.test_internal_note_is_not_exposed"
            ],
        )
        self.assertEqual(
            "add",
            scenario_g["expected_new_test_obligations"][0]["action"],
        )
        self.assertIn(
            "must be absent",
            scenario_g["evidence_rows"][2]["negative/absence"],
        )

    def test_runtime_staging_refuses_control_bundle_descendant(self) -> None:
        builder = self.load_builder()
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "q6"
            builder.build_all(output)

            with self.assertRaisesRegex(ValueError, "outside"):
                builder.stage_runtime_fixture(
                    output,
                    builder.CASE_SUPPORT_END,
                    output / "runtime" / builder.CASE_SUPPORT_END,
                )

    def test_runtime_staging_rejects_fixture_tampering(self) -> None:
        builder = self.load_builder()
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "q6"
            builder.build_all(output)
            fixture_file = (
                output
                / "fixtures"
                / builder.CASE_SUPPORT_END
                / "contract_app"
                / "current_contract.py"
            )
            fixture_file.write_text("# tampered\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "manifest mismatch"):
                builder.stage_runtime_fixture(
                    output,
                    builder.CASE_SUPPORT_END,
                    Path(temporary_directory) / "runtime" / builder.CASE_SUPPORT_END,
                )


if __name__ == "__main__":
    unittest.main()
