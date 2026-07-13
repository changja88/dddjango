from __future__ import annotations

import importlib.util
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / "dddjango" / "scripts"
MIGRATION_SCOPE = SCRIPTS / "migration_scope.py"
BOUNDARY_CHECK = SCRIPTS / "check-migration-boundary.py"
CATCH_ALL_CHECK = SCRIPTS / "check-catch-all-handler.py"


class MigrationScopeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.workspace = Path(self.temporary_directory.name)
        self.project = self.workspace / "project"
        self.project.mkdir()
        self.project = self.project.resolve()
        self.state = self.workspace / "boundary.json"

        spec = importlib.util.spec_from_file_location(
            f"dddjango_migration_scope_{id(self)}",
            MIGRATION_SCOPE,
        )
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        self.scope = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.scope)

    def write_scope(
        self,
        roots: list[str],
        root: Path | None = None,
        alias_targets: list[str] | None = None,
        external_owned_opaque_paths: list[str] | None = None,
    ) -> None:
        manifest = {
            "external_owned_opaque_paths": external_owned_opaque_paths or [],
            "format": "dddjango-migration-boundary-v11",
            "migration_alias_targets": alias_targets or [],
            "migration_roots": roots,
            "root": str((root or self.project).resolve()),
        }
        serialized = (
            json.dumps(manifest, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        self.state.write_bytes(serialized)
        receipt = {
            "format": "dddjango-migration-boundary-receipt-v2",
            "manifest_sha256": hashlib.sha256(serialized).hexdigest(),
            "state_path": str(self.state),
        }
        self.state.with_name(f"{self.state.name}.write-once").write_text(
            json.dumps(receipt, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def scoped_environment(self) -> dict[str, str]:
        environment = os.environ.copy()
        environment["DDDJANGO_G0_BOUNDARY_STATE"] = str(self.state)
        environment["DDDJANGO_EXTERNAL_OWNED_OPAQUE_PATHS_JSON"] = "[]"
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return environment

    def test_exact_roots_are_excluded_without_name_inference(self) -> None:
        custom = self.project / "schema_history" / "orders"
        custom.mkdir(parents=True)
        custom_file = custom / "0001.py"
        custom_file.write_text("operations = []\n", encoding="utf-8")
        ordinary = (
            self.project
            / "application"
            / "orders"
            / "domain_layer"
            / "migrations"
            / "rule.py"
        )
        ordinary.parent.mkdir(parents=True)
        ordinary.write_text("RULE = 'current'\n", encoding="utf-8")
        alias = self.project / "alias.py"
        alias.symlink_to(custom_file)
        self.write_scope(["schema_history/orders"])

        with mock.patch.dict(
            os.environ,
            {"DDDJANGO_G0_BOUNDARY_STATE": str(self.state)},
            clear=False,
        ):
            self.assertTrue(
                self.scope.is_migration_owned_path(self.project.resolve(), custom_file)
            )
            self.assertTrue(
                self.scope.is_migration_owned_path(self.project.resolve(), alias)
            )
            self.assertFalse(
                self.scope.is_migration_owned_path(self.project.resolve(), ordinary)
            )
            discovered = list(
                self.scope.iter_non_migration_files(
                    self.project.resolve(),
                    name_pattern="*.py",
                )
            )

        self.assertIn(ordinary, discovered)
        self.assertNotIn(custom_file, discovered)
        self.assertNotIn(alias, discovered)

    def test_internal_symlink_root_also_excludes_its_target_path(self) -> None:
        target = self.project / "shared" / "history"
        target.mkdir(parents=True)
        trap = target / "semantic_read_trap.py"
        os.mkfifo(trap)
        app = self.project / "orders"
        app.mkdir()
        (app / "migrations").symlink_to(target, target_is_directory=True)
        self.write_scope(["orders/migrations"])

        with mock.patch.dict(
            os.environ,
            {"DDDJANGO_G0_BOUNDARY_STATE": str(self.state)},
            clear=False,
        ):
            self.assertTrue(
                self.scope.is_migration_owned_path(self.project, trap)
            )
            discovered = list(
                self.scope.iter_non_migration_files(
                    self.project,
                    name_pattern="*.py",
                )
            )

        self.assertNotIn(trap, discovered)

    def test_manifest_alias_targets_and_external_owned_files_are_pruned(self) -> None:
        alias_target = self.project / "shared" / "history"
        alias_target.mkdir(parents=True)
        external_owned = self.project / "qa" / "migration_test.py"
        external_owned.parent.mkdir()
        trigger = (
            "@api.exception_handler(ValueError)\n"
            "def handle_value_error(request, exc):\n"
            "    return None\n"
        )
        (alias_target / "handler.py").write_text(trigger, encoding="utf-8")
        external_owned.write_text(trigger, encoding="utf-8")
        self.write_scope(
            [],
            alias_targets=["shared/history"],
            external_owned_opaque_paths=["qa/migration_test.py"],
        )

        result = subprocess.run(
            [sys.executable, str(CATCH_ALL_CHECK), str(self.project)],
            capture_output=True,
            text=True,
            check=False,
            env=self.scoped_environment(),
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_whole_project_scope_is_rejected(self) -> None:
        self.write_scope([], external_owned_opaque_paths=["."])

        with mock.patch.dict(
            os.environ,
            {"DDDJANGO_G0_BOUNDARY_STATE": str(self.state)},
            clear=False,
        ):
            with self.assertRaises(self.scope.MigrationScopeError):
                self.scope.require_migration_scope(self.project)

    def test_missing_or_wrong_root_state_fails_closed(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(self.scope.MigrationScopeError):
                self.scope.require_migration_scope(self.project.resolve())

        other = self.workspace / "other"
        other.mkdir()
        self.write_scope([], root=other)
        with mock.patch.dict(
            os.environ,
            {"DDDJANGO_G0_BOUNDARY_STATE": str(self.state)},
            clear=False,
        ):
            with self.assertRaises(self.scope.MigrationScopeError):
                self.scope.require_migration_scope(self.project.resolve())

    def test_all_seventeen_general_backstops_prune_standard_and_custom_roots(self) -> None:
        roots = ["orders/migrations", "schema_history/orders"]
        for relative in roots:
            directory = self.project / relative
            directory.mkdir(parents=True)
            os.mkfifo(directory / "semantic_read_trap.py")
        self.write_scope(roots)
        general_checks = sorted(
            path
            for path in SCRIPTS.glob("check-*.py")
            if path.name not in {
                "check-layer-skeleton.py",
                "check-migration-boundary.py",
            }
        )
        self.assertEqual(17, len(general_checks))

        for script in general_checks:
            with self.subTest(script=script.name):
                result = subprocess.run(
                    [sys.executable, str(script), str(self.project)],
                    capture_output=True,
                    text=True,
                    check=False,
                    env=self.scoped_environment(),
                    timeout=3,
                )
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_checker_skips_exact_root_but_checks_ordinary_migrations_named_folder(self) -> None:
        custom = self.project / "schema_history" / "orders"
        custom.mkdir(parents=True)
        trigger = (
            "@api.exception_handler(ValueError)\n"
            "def handle_value_error(request, exc):\n"
            "    return None\n"
        )
        (custom / "handler.py").write_text(trigger, encoding="utf-8")
        alias = self.project / "alias_handler.py"
        alias.symlink_to(custom / "handler.py")
        self.write_scope(["schema_history/orders"])

        exact_result = subprocess.run(
            [sys.executable, str(CATCH_ALL_CHECK), str(self.project)],
            capture_output=True,
            text=True,
            check=False,
            env=self.scoped_environment(),
        )
        self.assertEqual(0, exact_result.returncode, exact_result.stdout + exact_result.stderr)

        ordinary = (
            self.project
            / "application"
            / "orders"
            / "domain_layer"
            / "migrations"
        )
        ordinary.mkdir(parents=True)
        (ordinary / "handler.py").write_text(trigger, encoding="utf-8")
        ordinary_result = subprocess.run(
            [sys.executable, str(CATCH_ALL_CHECK), str(self.project)],
            capture_output=True,
            text=True,
            check=False,
            env=self.scoped_environment(),
        )

        self.assertEqual(
            2,
            ordinary_result.returncode,
            ordinary_result.stdout + ordinary_result.stderr,
        )
        self.assertIn(
            "application/orders/domain_layer/migrations/handler.py",
            ordinary_result.stdout,
        )

    def test_general_checker_requires_g0_scope_before_scanning(self) -> None:
        environment = os.environ.copy()
        environment.pop("DDDJANGO_G0_BOUNDARY_STATE", None)
        result = subprocess.run(
            [sys.executable, str(CATCH_ALL_CHECK), str(self.project)],
            capture_output=True,
            text=True,
            check=False,
            env=environment,
        )

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("DDDJANGO_G0_BOUNDARY_STATE가 없다", result.stderr)

    def test_external_layer_root_does_not_change_common_container_semantics(self) -> None:
        common = self.project / "application" / "common"
        common.mkdir(parents=True)
        (common / "problem.py").write_text("VALUE = 'current'\n", encoding="utf-8")
        (common / "domain_layer").mkdir()
        self.write_scope(["application/common/domain_layer"])

        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "check-common-container.py"),
                str(self.project),
            ],
            capture_output=True,
            text=True,
            check=False,
            env=self.scoped_environment(),
        )

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("application/common", result.stdout)

    def test_layer_and_snapshot_do_not_read_custom_models_package(self) -> None:
        django_app = (
            self.project
            / "application"
            / "orders"
            / "infra_layer"
            / "django_orders"
        )
        models = django_app / "models"
        models.mkdir(parents=True)
        (django_app / "apps.py").write_text(
            "from django.apps import AppConfig\n"
            "class OrdersConfig(AppConfig):\n"
            "    name = 'application.orders.infra_layer.django_orders'\n",
            encoding="utf-8",
        )
        os.mkfifo(models / "semantic_read_trap.py")
        (self.project / "settings.py").write_text(
            "MIGRATION_MODULES = {"
            "'orders': 'application.orders.infra_layer.django_orders.models'"
            "}\n",
            encoding="utf-8",
        )

        snapshot = subprocess.run(
            [
                sys.executable,
                str(BOUNDARY_CHECK),
                "snapshot",
                str(self.project),
                str(self.state),
            ],
            capture_output=True,
            text=True,
            check=False,
            env=self.scoped_environment(),
            timeout=3,
        )
        self.assertEqual(0, snapshot.returncode, snapshot.stdout + snapshot.stderr)
        layer = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "check-layer-skeleton.py"),
                str(self.project),
                str(self.state),
            ],
            capture_output=True,
            text=True,
            check=False,
            env=self.scoped_environment(),
            timeout=3,
        )

        self.assertEqual(0, layer.returncode, layer.stdout + layer.stderr)

    def test_boundary_state_drives_all_eighteen_non_boundary_scripts(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(BOUNDARY_CHECK),
                "snapshot",
                str(self.project),
                str(self.state),
            ],
            capture_output=True,
            text=True,
            check=False,
            env=self.scoped_environment(),
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        scripts = sorted(
            path
            for path in SCRIPTS.glob("check-*.py")
            if path.name != "check-migration-boundary.py"
        )
        self.assertEqual(18, len(scripts))

        for script in scripts:
            command = [sys.executable, str(script), str(self.project)]
            if script.name == "check-layer-skeleton.py":
                command.append(str(self.state))
            with self.subTest(script=script.name):
                execution = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    check=False,
                    env=self.scoped_environment(),
                )
                self.assertEqual(
                    0,
                    execution.returncode,
                    execution.stdout + execution.stderr,
                )


if __name__ == "__main__":
    unittest.main()
