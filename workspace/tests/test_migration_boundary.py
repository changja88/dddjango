from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATION_CHECK = REPO_ROOT / "dddjango" / "scripts" / "check-migration-boundary.py"
LAYER_CHECK = REPO_ROOT / "dddjango" / "scripts" / "check-layer-skeleton.py"


class MigrationBoundaryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.workspace = Path(self.temporary_directory.name)
        self.project = self.workspace / "project"
        self.project.mkdir()
        self.state = self.workspace / "boundary.json"

    def run_boundary(
        self,
        action: str,
        boundary_path: Path | None = None,
        external_owned_opaque_paths: list[str] | None = None,
        timeout: float | None = None,
    ) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["DDDJANGO_EXTERNAL_OWNED_OPAQUE_PATHS_JSON"] = json.dumps(
            external_owned_opaque_paths or [],
            separators=(",", ":"),
        )
        return subprocess.run(
            [
                sys.executable,
                str(MIGRATION_CHECK),
                action,
                str(self.project),
                str(boundary_path or self.state),
            ],
            capture_output=True,
            text=True,
            check=False,
            env=environment,
            timeout=timeout,
        )

    def snapshot(self) -> None:
        result = self.run_boundary("snapshot")
        self.assertEqual(0, result.returncode, result.stderr)

    def commit_project_baseline(self) -> None:
        commands = (
            ["git", "init", "-q"],
            ["git", "add", "."],
            [
                "git",
                "-c",
                "user.name=dddjango-test",
                "-c",
                "user.email=dddjango@example.invalid",
                "commit",
                "-q",
                "-m",
                "baseline",
            ],
        )
        for command in commands:
            result = subprocess.run(
                command,
                cwd=self.project,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def assert_boundary_blocked(self, expected_path: str) -> None:
        result = self.run_boundary("verify")
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn(expected_path, result.stdout)

    def declare_settings_module(self, module: str) -> None:
        (self.project / "manage.py").write_text(
            "import os\n"
            f"os.environ.setdefault('DJANGO_SETTINGS_MODULE', {module!r})\n",
            encoding="utf-8",
        )

    def make_app(self, name: str) -> Path:
        app = self.project / name
        app.mkdir(parents=True)
        (app / "__init__.py").write_text("", encoding="utf-8")
        (app / "apps.py").write_text(
            "from django.apps import AppConfig\n\n"
            "class Config(AppConfig):\n"
            f"    name = {name!r}\n",
            encoding="utf-8",
        )
        (app / "models.py").write_text("class Order: pass\n", encoding="utf-8")
        return app

    def make_migrations(self, app_name: str = "orders") -> Path:
        app = self.make_app(app_name)
        migrations = app / "migrations"
        migrations.mkdir()
        (migrations / "__init__.py").write_text("", encoding="utf-8")
        (migrations / "0001_initial.py").write_text("operations = []\n", encoding="utf-8")
        return migrations

    def make_complete_flat_persistence_bc(self, name: str = "orders") -> Path:
        bc = self.project / "application" / name
        bc.mkdir(parents=True)
        (bc / "models.py").write_text(
            "from django.db import models\n"
            "class Record(models.Model):\n"
            "    pass\n",
            encoding="utf-8",
        )
        for layer in (
            "domain_layer",
            "application_layer",
            "infra_layer",
            "presentation_layer",
        ):
            directory = bc / layer
            directory.mkdir()
            (directory / "__init__.py").write_text("", encoding="utf-8")
        for relative in (
            "presentation_layer/api",
            "presentation_layer/schema",
            "infra_layer/acl",
        ):
            directory = bc / relative
            directory.mkdir()
            (directory / "__init__.py").write_text("", encoding="utf-8")
        return bc

    def test_ordinary_application_edit_keeps_boundary_clean(self) -> None:
        app = self.make_app("orders")
        self.snapshot()

        (app / "service.py").write_text("def place_order(): return None\n", encoding="utf-8")
        (app / "models.py").write_text("class CurrentOrder: pass\n", encoding="utf-8")

        result = self.run_boundary("verify")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_numbered_general_python_package_is_not_misclassified(self) -> None:
        reports = self.project / "reports"
        reports.mkdir()
        (reports / "__init__.py").write_text("", encoding="utf-8")
        report = reports / "2024_report.py"
        report.write_text("VALUE = 1\n", encoding="utf-8")
        self.snapshot()

        report.write_text("VALUE = 2\n", encoding="utf-8")

        result = self.run_boundary("verify")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_package_with_0001_module_is_not_guessed_as_migrations(self) -> None:
        examples = self.project / "examples"
        examples.mkdir()
        (examples / "__init__.py").write_text("", encoding="utf-8")
        numbered = examples / "0001.py"
        numbered.write_text("VALUE = 1\n", encoding="utf-8")
        self.snapshot()

        numbered.write_text("VALUE = 2\n", encoding="utf-8")

        result = self.run_boundary("verify")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_non_django_documentation_migrations_directory_is_not_frozen(self) -> None:
        documentation = self.project / "docs" / "migrations"
        documentation.mkdir(parents=True)
        guide = documentation / "guide.md"
        guide.write_text("old guidance\n", encoding="utf-8")
        self.snapshot()

        guide.write_text("current guidance\n", encoding="utf-8")

        result = self.run_boundary("verify")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_non_django_models_and_migrations_tree_is_not_frozen(self) -> None:
        pipeline = self.project / "data_pipeline"
        migrations = pipeline / "migrations"
        migrations.mkdir(parents=True)
        (pipeline / "models.py").write_text("class Record: pass\n", encoding="utf-8")
        guide = migrations / "guide.sql"
        guide.write_text("select 'old';\n", encoding="utf-8")
        self.snapshot()

        guide.write_text("select 'current';\n", encoding="utf-8")

        result = self.run_boundary("verify")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_standard_migration_structural_traps_are_never_semantically_read(self) -> None:
        app = self.make_app("orders")
        migrations = app / "migrations"
        migrations.mkdir()
        for name in ("apps.py", "manage.py", "asgi.py", "wsgi.py"):
            try:
                os.mkfifo(migrations / name)
            except OSError as error:
                self.skipTest(f"fifo unavailable: {error}")

        preflight = self.run_boundary("preflight", timeout=5)
        snapshot = self.run_boundary("snapshot", timeout=5)

        self.assertEqual(0, preflight.returncode, preflight.stdout + preflight.stderr)
        self.assertIn('"migration_roots":["orders/migrations"]', preflight.stdout)
        self.assertEqual(0, snapshot.returncode, snapshot.stdout + snapshot.stderr)

    def test_empty_migrations_directory_added_after_snapshot_is_blocked(self) -> None:
        app = self.make_app("orders")
        self.snapshot()

        (app / "migrations").mkdir()

        self.assert_boundary_blocked("orders/migrations")

    def test_nested_skip_named_directory_inside_migrations_is_not_skipped(self) -> None:
        migrations = self.make_migrations()
        cache = migrations / "cache"
        cache.mkdir()
        migration = cache / "0002_cached.py"
        migration.write_text("operations = []\n", encoding="utf-8")
        self.snapshot()

        migration.write_text("operations = ['changed']\n", encoding="utf-8")

        self.assert_boundary_blocked("orders/migrations/cache/0002_cached.py")

    def test_import_generated_python_cache_does_not_change_boundary(self) -> None:
        migrations = self.make_migrations()
        migration = migrations / "0001_initial.py"
        self.snapshot()

        imported = subprocess.run(
            [
                sys.executable,
                "-c",
                "import importlib; importlib.import_module('orders.migrations.0001_initial')",
            ],
            cwd=self.project,
            env={
                key: value
                for key, value in os.environ.items()
                if key != "PYTHONDONTWRITEBYTECODE"
            },
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, imported.returncode, imported.stdout + imported.stderr)
        self.assertTrue((migrations / "__pycache__").is_dir())
        clean = self.run_boundary("verify")
        self.assertEqual(0, clean.returncode, clean.stdout + clean.stderr)

        migration.write_text("operations = ['changed']\n", encoding="utf-8")
        self.assert_boundary_blocked("orders/migrations/0001_initial.py")

    def test_bytecode_outside_python_cache_directory_is_tracked(self) -> None:
        migrations = self.make_migrations()
        self.snapshot()

        (migrations / "0002_hidden.pyc").write_bytes(b"opaque-bytecode")

        self.assert_boundary_blocked("orders/migrations/0002_hidden.pyc")

    def test_symlinked_migration_root_python_cache_is_ignored(self) -> None:
        app = self.make_app("orders")
        external = self.workspace / "external_migrations"
        external.mkdir()
        (external / "__init__.py").write_text("", encoding="utf-8")
        (external / "0001_initial.py").write_text("operations = []\n", encoding="utf-8")
        try:
            (app / "migrations").symlink_to(external, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")
        self.snapshot()

        imported = subprocess.run(
            [
                sys.executable,
                "-c",
                "import importlib; importlib.import_module('orders.migrations.0001_initial')",
            ],
            cwd=self.project,
            env={
                key: value
                for key, value in os.environ.items()
                if key != "PYTHONDONTWRITEBYTECODE"
            },
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, imported.returncode, imported.stdout + imported.stderr)
        self.assertTrue((external / "__pycache__").is_dir())

        clean = self.run_boundary("verify")
        self.assertEqual(0, clean.returncode, clean.stdout + clean.stderr)

    def test_static_registered_skip_named_app_migration_change_is_blocked(self) -> None:
        (self.project / "settings.py").write_text(
            "INSTALLED_APPS = ['venv.apps.VenvConfig']\n",
            encoding="utf-8",
        )
        app = self.project / "venv"
        app.mkdir()
        (app / "apps.py").write_text(
            "from django.apps import AppConfig\n\n"
            "class VenvConfig(AppConfig):\n"
            "    name = 'venv'\n",
            encoding="utf-8",
        )
        migrations = app / "migrations"
        migrations.mkdir()
        migration = migrations / "0001_initial.py"
        migration.write_text("operations = []\n", encoding="utf-8")
        self.snapshot()

        migration.write_text("operations = ['changed']\n", encoding="utf-8")

        self.assert_boundary_blocked("venv/migrations/0001_initial.py")

    def test_registered_app_below_skip_named_ancestor_is_blocked(self) -> None:
        (self.project / "settings.py").write_text(
            "INSTALLED_APPS = ['vendor.venv.orders.apps.OrdersConfig']\n",
            encoding="utf-8",
        )
        app = self.project / "vendor" / "venv" / "orders"
        app.mkdir(parents=True)
        (app / "apps.py").write_text(
            "from django.apps import AppConfig\n\n"
            "class OrdersConfig(AppConfig):\n"
            "    name = 'vendor.venv.orders'\n",
            encoding="utf-8",
        )
        migrations = app / "migrations"
        migrations.mkdir()
        migration = migrations / "0001_initial.py"
        migration.write_text("operations = []\n", encoding="utf-8")
        self.snapshot()

        migration.write_text("operations = ['changed']\n", encoding="utf-8")

        self.assert_boundary_blocked(
            "vendor/venv/orders/migrations/0001_initial.py"
        )

    def test_src_entrypoint_settings_tracks_app_below_skip_ancestor(self) -> None:
        (self.project / "manage.py").write_text(
            "import os\n"
            "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_settings')\n",
            encoding="utf-8",
        )
        source_root = self.project / "src"
        source_root.mkdir()
        (source_root / "project_settings.py").write_text(
            "INSTALLED_APPS = ['vendor.venv.orders.apps.OrdersConfig']\n",
            encoding="utf-8",
        )
        app = source_root / "vendor" / "venv" / "orders"
        app.mkdir(parents=True)
        (app / "apps.py").write_text(
            "from django.apps import AppConfig\n"
            "class OrdersConfig(AppConfig):\n"
            "    name = 'vendor.venv.orders'\n",
            encoding="utf-8",
        )
        migrations = app / "migrations"
        migrations.mkdir()
        migration = migrations / "0001_initial.py"
        migration.write_text("operations = []\n", encoding="utf-8")
        self.snapshot()

        migration.write_text("operations = ['changed']\n", encoding="utf-8")

        self.assert_boundary_blocked(
            "src/vendor/venv/orders/migrations/0001_initial.py"
        )

    def test_symlinked_migration_file_target_change_is_blocked(self) -> None:
        migrations = self.make_migrations()
        shared = self.project / "shared"
        shared.mkdir()
        target = shared / "linked_migration.py"
        target.write_text("operations = []\n", encoding="utf-8")
        link = migrations / "0002_linked.py"
        try:
            link.symlink_to(target)
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")
        self.snapshot()

        target.write_text("operations = ['changed']\n", encoding="utf-8")

        self.assert_boundary_blocked("orders/migrations/0002_linked.py")

    def test_external_symlink_target_content_is_not_read_or_tracked(self) -> None:
        migrations = self.make_migrations()
        target = self.workspace / "external_migration.py"
        target.write_text("operations = []\n", encoding="utf-8")
        link = migrations / "0002_external.py"
        try:
            link.symlink_to(target)
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")
        self.snapshot()

        manifest_text = self.state.read_text(encoding="utf-8")
        self.assertNotIn(str(target), manifest_text)
        target.write_text("operations = ['changed']\n", encoding="utf-8")

        result = self.run_boundary("verify")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_external_symlinked_app_target_change_is_not_tracked(self) -> None:
        external_app = self.workspace / "external_app"
        migrations = external_app / "migrations"
        migrations.mkdir(parents=True)
        (external_app / "models.py").write_text("class Legacy: pass\n", encoding="utf-8")
        (migrations / "__init__.py").write_text("", encoding="utf-8")
        migration = migrations / "0001_initial.py"
        migration.write_text("operations = []\n", encoding="utf-8")
        link = self.project / "linked_app"
        try:
            link.symlink_to(external_app, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")
        (self.project / "settings.py").write_text(
            "INSTALLED_APPS = ['linked_app']\n",
            encoding="utf-8",
        )
        self.snapshot()

        migration.write_text("operations = ['changed']\n", encoding="utf-8")

        result = self.run_boundary("verify")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_nested_external_symlink_target_change_is_not_tracked(self) -> None:
        external_app = self.workspace / "external_app"
        external_app.mkdir()
        (external_app / "models.py").write_text("class Legacy: pass\n", encoding="utf-8")
        migration_target = self.workspace / "external_migrations"
        migration_target.mkdir()
        migration = migration_target / "0001_initial.py"
        migration.write_text("operations = []\n", encoding="utf-8")
        try:
            (external_app / "migrations").symlink_to(
                migration_target,
                target_is_directory=True,
            )
            (self.project / "linked_app").symlink_to(
                external_app,
                target_is_directory=True,
            )
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")
        (self.project / "settings.py").write_text(
            "INSTALLED_APPS = ['linked_app']\n",
            encoding="utf-8",
        )
        self.snapshot()

        migration.write_text("operations = ['changed']\n", encoding="utf-8")

        result = self.run_boundary("verify")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_two_level_external_symlink_target_change_is_not_tracked(self) -> None:
        actual_app = self.workspace / "actual_app"
        migrations = actual_app / "migrations"
        migrations.mkdir(parents=True)
        (actual_app / "models.py").write_text("class Order: pass\n", encoding="utf-8")
        migration = migrations / "0001_initial.py"
        migration.write_text("operations = []\n", encoding="utf-8")
        outer = self.workspace / "outer"
        packages = outer / "packages"
        packages.mkdir(parents=True)
        try:
            (packages / "orders").symlink_to(actual_app, target_is_directory=True)
            (self.project / "linked_root").symlink_to(
                outer,
                target_is_directory=True,
            )
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")
        (self.project / "settings.py").write_text(
            "INSTALLED_APPS = ['linked_root.packages.orders']\n",
            encoding="utf-8",
        )
        self.snapshot()

        migration.write_text("operations = ['changed']\n", encoding="utf-8")

        result = self.run_boundary("verify")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_symlinked_app_retarget_is_blocked_even_with_same_bytes(self) -> None:
        external_apps: list[Path] = []
        for name in ("external_a", "external_b"):
            external_app = self.workspace / name
            migrations = external_app / "migrations"
            migrations.mkdir(parents=True)
            (migrations / "__init__.py").write_text("", encoding="utf-8")
            (external_app / "models.py").write_text(
                "class Legacy: pass\n",
                encoding="utf-8",
            )
            (migrations / "0001_initial.py").write_text(
                "operations = []\n",
                encoding="utf-8",
            )
            external_apps.append(external_app)
        link = self.project / "linked_app"
        try:
            link.symlink_to(external_apps[0], target_is_directory=True)
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")
        (self.project / "settings.py").write_text(
            "INSTALLED_APPS = ['linked_app']\n",
            encoding="utf-8",
        )
        self.snapshot()

        link.unlink()
        link.symlink_to(external_apps[1], target_is_directory=True)

        self.assert_boundary_blocked(".dddjango-app-directory-link/linked_app")

    def test_custom_migration_modules_content_change_is_blocked(self) -> None:
        self.declare_settings_module("config.settings")
        settings = self.project / "config"
        settings.mkdir()
        (settings / "settings.py").write_text(
            'MIGRATION_MODULES = {"orders": "schema_history.orders"}\n',
            encoding="utf-8",
        )
        custom = self.project / "schema_history" / "orders"
        custom.mkdir(parents=True)
        (custom / "__init__.py").write_text("", encoding="utf-8")
        migration = custom / "0001_initial.py"
        migration.write_text("operations = []\n", encoding="utf-8")
        self.snapshot()

        migration.write_text("operations = ['changed']\n", encoding="utf-8")

        self.assert_boundary_blocked("schema_history/orders/0001_initial.py")

    def test_custom_root_structural_entrypoint_overlap_fails_without_reading(self) -> None:
        self.declare_settings_module("project.settings")
        project_package = self.project / "project"
        project_package.mkdir()
        (project_package / "settings.py").write_text(
            "MIGRATION_MODULES = {'orders': 'project'}\n",
            encoding="utf-8",
        )
        trap = project_package / "asgi.py"
        try:
            os.mkfifo(trap)
        except OSError as error:
            self.skipTest(f"fifo unavailable: {error}")

        result = self.run_boundary("preflight", timeout=5)

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("structural discovery source", result.stderr)

    def test_custom_root_cannot_hide_registered_application_sources(self) -> None:
        (self.project / "settings.py").write_text(
            "INSTALLED_APPS = ['app.apps.AppConfig']\n"
            "MIGRATION_MODULES = {'app': 'app'}\n",
            encoding="utf-8",
        )
        app = self.project / "app"
        app.mkdir()
        (app / "apps.py").write_text(
            "from django.apps import AppConfig as DjangoAppConfig\n"
            "class AppConfig(DjangoAppConfig):\n"
            "    name = 'app'\n",
            encoding="utf-8",
        )
        (app / "models.py").write_text("class Record: pass\n", encoding="utf-8")

        result = self.run_boundary("preflight", timeout=5)

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("structural discovery source", result.stderr)

    def test_dynamic_migration_modules_fails_closed(self) -> None:
        (self.project / "settings.py").write_text(
            "def custom_root():\n"
            "    return 'schema_history.orders'\n"
            "MIGRATION_MODULES = {'orders': custom_root()}\n",
            encoding="utf-8",
        )

        result = self.run_boundary("preflight")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("MIGRATION_MODULES", result.stderr)
        self.assertIn("정적", result.stderr)

    def test_dynamic_installed_apps_fails_closed(self) -> None:
        (self.project / "settings.py").write_text(
            "def installed_apps():\n"
            "    return ['orders']\n"
            "INSTALLED_APPS = installed_apps()\n",
            encoding="utf-8",
        )

        result = self.run_boundary("preflight")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("INSTALLED_APPS", result.stderr)
        self.assertIn("정적", result.stderr)

    def test_dynamic_settings_module_fails_closed(self) -> None:
        (self.project / "manage.py").write_text(
            "import os\n"
            "os.environ.setdefault(\n"
            "    'DJANGO_SETTINGS_MODULE', os.environ.get('PROJECT_SETTINGS')\n"
            ")\n",
            encoding="utf-8",
        )

        result = self.run_boundary("preflight")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("DJANGO_SETTINGS_MODULE", result.stderr)
        self.assertIn("정적", result.stderr)

    def test_common_static_settings_composition_is_supported(self) -> None:
        (self.project / "manage.py").write_text(
            "import os\n"
            "SETTINGS = 'project' + '.settings'\n"
            "os.environ.setdefault('DJANGO_SETTINGS_MODULE', SETTINGS)\n",
            encoding="utf-8",
        )
        project_package = self.project / "project"
        project_package.mkdir()
        (project_package / "settings.py").write_text(
            "DJANGO_APPS = ['django.contrib.auth']\n"
            "THIRD_PARTY_APPS = []\n"
            "LOCAL_APPS = ['orders']\n"
            "INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS\n"
            "CUSTOM_ROOT = 'schema_history' + '.orders'\n"
            "MIGRATION_MODULES = {'orders': CUSTOM_ROOT}\n",
            encoding="utf-8",
        )
        app = self.project / "orders"
        app.mkdir()
        (app / "models.py").write_text("class Order: pass\n", encoding="utf-8")
        standard = app / "migrations"
        standard.mkdir()
        custom = self.project / "schema_history" / "orders"
        custom.mkdir(parents=True)
        (custom / "0001_initial.py").write_text(
            "operations = []\n",
            encoding="utf-8",
        )

        result = self.run_boundary("preflight")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn('"schema_history/orders"', result.stdout)

    def test_direct_mutable_installed_apps_alias_fails_closed(self) -> None:
        (self.project / "settings.py").write_text(
            "LOCAL_APPS = ['orders']\n"
            "INSTALLED_APPS = LOCAL_APPS\n"
            "LOCAL_APPS = []\n",
            encoding="utf-8",
        )
        migrations = self.project / "orders" / "migrations"
        migrations.mkdir(parents=True)
        (migrations / "0001_initial.py").write_text(
            "operations = []\n",
            encoding="utf-8",
        )

        result = self.run_boundary("preflight")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("Name alias", result.stderr)

    def test_mutated_installed_apps_alias_fails_closed(self) -> None:
        (self.project / "settings.py").write_text(
            "LOCAL_APPS = []\n"
            "INSTALLED_APPS = LOCAL_APPS\n"
            "LOCAL_APPS.append('orders')\n",
            encoding="utf-8",
        )

        result = self.run_boundary("preflight")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("Name alias", result.stderr)

    def test_indirect_mutated_installed_apps_alias_fails_closed(self) -> None:
        (self.project / "settings.py").write_text(
            "LOCAL_APPS = []\n"
            "ALIAS = LOCAL_APPS\n"
            "ALIAS.append('orders')\n"
            "INSTALLED_APPS = LOCAL_APPS + []\n",
            encoding="utf-8",
        )

        result = self.run_boundary("preflight")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("재할당·변이", result.stderr)

    def test_control_flow_rebound_installed_apps_dependency_fails_closed(self) -> None:
        (self.project / "settings.py").write_text(
            "LOCAL_APPS = []\n"
            "if True:\n"
            "    LOCAL_APPS = ['orders']\n"
            "INSTALLED_APPS = LOCAL_APPS + []\n",
            encoding="utf-8",
        )

        result = self.run_boundary("preflight")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("재할당·변이", result.stderr)

    def test_container_alias_mutation_fails_closed(self) -> None:
        (self.project / "settings.py").write_text(
            "LOCAL_APPS = []\n"
            "WRAPPER = [LOCAL_APPS]\n"
            "WRAPPER[0].append('orders')\n"
            "INSTALLED_APPS = LOCAL_APPS + []\n",
            encoding="utf-8",
        )

        result = self.run_boundary("preflight")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("재할당·변이", result.stderr)

    def test_reassigned_nested_migration_alias_fails_closed(self) -> None:
        (self.project / "settings.py").write_text(
            "ROOT = 'schema_history.orders'\n"
            "BASE = {'orders': ROOT}\n"
            "ROOT = 'other_history.orders'\n"
            "MIGRATION_MODULES = BASE\n",
            encoding="utf-8",
        )

        result = self.run_boundary("preflight")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("Name alias", result.stderr)

    def test_installed_apps_method_mutation_fails_closed(self) -> None:
        (self.project / "settings.py").write_text(
            "INSTALLED_APPS = []\n"
            "INSTALLED_APPS.append('orders')\n",
            encoding="utf-8",
        )

        result = self.run_boundary("preflight")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("method/subscript mutation", result.stderr)

    def test_migration_modules_method_mutation_fails_closed(self) -> None:
        (self.project / "settings.py").write_text(
            "MIGRATION_MODULES = {}\n"
            "MIGRATION_MODULES.update({'orders': 'schema_history.orders'})\n",
            encoding="utf-8",
        )

        result = self.run_boundary("preflight")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("method/subscript mutation", result.stderr)

    def test_symlinked_manage_entrypoint_fails_closed(self) -> None:
        bootstrap = self.project / "bootstrap.py"
        bootstrap.write_text(
            "import os\n"
            "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')\n",
            encoding="utf-8",
        )
        try:
            (self.project / "manage.py").symlink_to(bootstrap)
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")
        project_package = self.project / "project"
        project_package.mkdir()
        (project_package / "settings.py").write_text(
            "MIGRATION_MODULES = {'orders': 'schema_history.orders'}\n",
            encoding="utf-8",
        )
        custom = self.project / "schema_history" / "orders"
        custom.mkdir(parents=True)
        (custom / "0001_initial.py").write_text(
            "operations = []\n",
            encoding="utf-8",
        )

        result = self.run_boundary("preflight", timeout=5)

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("entrypoint symlink", result.stderr)

    def test_app_config_symlink_into_migrations_fails_without_reading(self) -> None:
        (self.project / "settings.py").write_text(
            "INSTALLED_APPS = ['orders']\n",
            encoding="utf-8",
        )
        app = self.project / "orders"
        migrations = app / "migrations"
        migrations.mkdir(parents=True)
        (app / "models.py").write_text("class Order: pass\n", encoding="utf-8")
        trap = migrations / "trap.py"
        try:
            os.mkfifo(trap)
            (app / "apps.py").symlink_to(trap)
        except OSError as error:
            self.skipTest(f"fifo or symlink unavailable: {error}")

        result = self.run_boundary("preflight", timeout=5)

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("opaque migration", result.stderr)

    def test_settings_symlink_into_migrations_fails_without_reading(self) -> None:
        self.declare_settings_module("config.settings")
        migrations = self.project / "orders" / "migrations"
        migrations.mkdir(parents=True)
        (self.project / "orders" / "models.py").write_text(
            "class Order: pass\n",
            encoding="utf-8",
        )
        trap = migrations / "trap.py"
        config = self.project / "config"
        config.mkdir()
        try:
            os.mkfifo(trap)
            (config / "settings.py").symlink_to(trap)
        except OSError as error:
            self.skipTest(f"fifo or symlink unavailable: {error}")

        result = self.run_boundary("preflight", timeout=5)

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("opaque migration", result.stderr)

    def test_src_layout_custom_migration_modules_change_is_blocked(self) -> None:
        (self.project / "settings.py").write_text(
            'MIGRATION_MODULES = {"orders": "schema_history.orders"}\n',
            encoding="utf-8",
        )
        custom = self.project / "src" / "schema_history" / "orders"
        custom.mkdir(parents=True)
        (custom / "__init__.py").write_text("", encoding="utf-8")
        migration = custom / "0001_initial.py"
        migration.write_text("operations = []\n", encoding="utf-8")
        self.snapshot()

        migration.write_text("operations = ['changed']\n", encoding="utf-8")

        self.assert_boundary_blocked("src/schema_history/orders/0001_initial.py")

    def test_custom_migration_root_ancestor_retarget_is_blocked(self) -> None:
        (self.project / "settings.py").write_text(
            'MIGRATION_MODULES = {"orders": "schema_history.orders"}\n',
            encoding="utf-8",
        )
        targets: list[Path] = []
        for name in ("history_a", "history_b"):
            target = self.workspace / name
            orders = target / "orders"
            orders.mkdir(parents=True)
            (orders / "__init__.py").write_text("", encoding="utf-8")
            (orders / "0001_initial.py").write_text(
                "operations = []\n",
                encoding="utf-8",
            )
            targets.append(target)
        link = self.project / "schema_history"
        try:
            link.symlink_to(targets[0], target_is_directory=True)
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")
        self.snapshot()

        link.unlink()
        link.symlink_to(targets[1], target_is_directory=True)

        self.assert_boundary_blocked(
            ".dddjango-explicit-root-link/schema_history"
        )

    def test_migration_modules_configuration_change_is_blocked(self) -> None:
        settings = self.project / "settings.py"
        settings.write_text(
            'MIGRATION_MODULES = {"orders": "schema_history.orders"}\n',
            encoding="utf-8",
        )
        self.snapshot()

        settings.write_text(
            'MIGRATION_MODULES = {"orders": "other_history.orders"}\n',
            encoding="utf-8",
        )

        self.assert_boundary_blocked(".dddjango-migration-config/settings.py")

    def test_migration_modules_source_reformat_is_blocked(self) -> None:
        settings = self.project / "settings.py"
        settings.write_text(
            'MIGRATION_MODULES = {"orders": "schema_history.orders"}\n',
            encoding="utf-8",
        )
        self.snapshot()

        settings.write_text(
            "MIGRATION_MODULES = {'orders': 'schema_history.orders'}  # reformatted\n",
            encoding="utf-8",
        )

        self.assert_boundary_blocked(".dddjango-migration-config/settings.py")

    def test_external_symlinked_settings_file_content_is_not_read(self) -> None:
        external = self.workspace / "external_settings.py"
        external.write_text(
            'MIGRATION_MODULES = {"orders": "history_a.orders"}\n',
            encoding="utf-8",
        )
        settings = self.project / "settings.py"
        try:
            settings.symlink_to(external)
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")
        self.snapshot()

        external.write_text(
            'MIGRATION_MODULES = {"orders": "history_b.orders"}\n',
            encoding="utf-8",
        )

        result = self.run_boundary("verify")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_external_symlinked_settings_directory_content_is_not_read(self) -> None:
        self.declare_settings_module("config.settings")
        external = self.workspace / "external_config"
        external.mkdir()
        source = external / "settings.py"
        source.write_text(
            'MIGRATION_MODULES = {"orders": "history_a.orders"}\n',
            encoding="utf-8",
        )
        config = self.project / "config"
        try:
            config.symlink_to(external, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")
        self.snapshot()

        source.write_text(
            'MIGRATION_MODULES = {"orders": "history_b.orders"}\n',
            encoding="utf-8",
        )

        result = self.run_boundary("verify")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_external_settings_do_not_declare_local_custom_migration_root(self) -> None:
        self.declare_settings_module("linked.config.settings")
        actual_settings = self.workspace / "actual_settings"
        actual_settings.mkdir()
        (actual_settings / "settings.py").write_text(
            "MIGRATION_MODULES = {'orders': 'schema_history.orders'}\n",
            encoding="utf-8",
        )
        outer = self.workspace / "outer_settings"
        outer.mkdir()
        try:
            (outer / "config").symlink_to(
                actual_settings,
                target_is_directory=True,
            )
            (self.project / "linked").symlink_to(outer, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")
        custom = self.project / "schema_history" / "orders"
        custom.mkdir(parents=True)
        migration = custom / "0001_initial.py"
        migration.write_text("operations = []\n", encoding="utf-8")
        self.snapshot()

        migration.write_text("operations = ['changed']\n", encoding="utf-8")

        result = self.run_boundary("verify")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_external_settings_link_retarget_is_blocked(self) -> None:
        self.declare_settings_module("config.settings")
        targets: list[Path] = []
        for name in ("settings_a", "settings_b"):
            target = self.workspace / name
            target.mkdir()
            (target / "settings.py").write_text(
                "MIGRATION_MODULES = {}\n",
                encoding="utf-8",
            )
            targets.append(target)
        config = self.project / "config"
        try:
            config.symlink_to(targets[0], target_is_directory=True)
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")
        self.snapshot()

        config.unlink()
        config.symlink_to(targets[1], target_is_directory=True)

        self.assert_boundary_blocked(".dddjango-settings-link/config")

    def test_invalid_python_with_migration_modules_token_is_not_configuration(self) -> None:
        scratch = self.project / "broken_example.py"
        scratch.write_text("MIGRATION_MODULES = {\n", encoding="utf-8")
        self.snapshot()

        scratch.write_text("MIGRATION_MODULES = {\n# still invalid\n", encoding="utf-8")

        result = self.run_boundary("verify")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_local_migration_modules_name_is_not_configuration(self) -> None:
        source = self.project / "helper.py"
        source.write_text(
            "def example():\n"
            '    MIGRATION_MODULES = {"orders": "schema_history.orders"}\n'
            "    return MIGRATION_MODULES\n",
            encoding="utf-8",
        )
        self.snapshot()

        source.write_text(
            "def example():\n"
            '    MIGRATION_MODULES = {"orders": "other_history.orders"}\n'
            "    return MIGRATION_MODULES\n",
            encoding="utf-8",
        )

        result = self.run_boundary("verify")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_unrelated_module_level_migration_modules_constant_is_not_settings(self) -> None:
        helper = self.project / "helper.py"
        helper.write_text(
            "MIGRATION_MODULES = {'example': 'not_project_settings'}\n",
            encoding="utf-8",
        )
        self.snapshot()

        helper.write_text(
            "MIGRATION_MODULES = {'example': 'still_not_project_settings'}\n",
            encoding="utf-8",
        )

        result = self.run_boundary("verify")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_documentation_settings_example_is_not_project_settings(self) -> None:
        example = self.project / "docs" / "settings" / "example.py"
        example.parent.mkdir(parents=True)
        example.write_text(
            "MIGRATION_MODULES = {'example': 'documented_history'}\n",
            encoding="utf-8",
        )
        self.snapshot()

        example.write_text(
            "MIGRATION_MODULES = {'example': 'updated_documented_history'}\n",
            encoding="utf-8",
        )

        result = self.run_boundary("verify")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_unrelated_entrypoint_call_does_not_declare_settings(self) -> None:
        (self.project / "manage.py").write_text(
            "def marker(key, value):\n"
            "    return (key, value)\n\n"
            "marker('DJANGO_SETTINGS_MODULE', 'config.runtime')\n",
            encoding="utf-8",
        )
        config = self.project / "config"
        config.mkdir()
        runtime = config / "runtime.py"
        runtime.write_text(
            "MIGRATION_MODULES = {'example': 'not_project_settings'}\n",
            encoding="utf-8",
        )
        self.snapshot()

        runtime.write_text(
            "MIGRATION_MODULES = {'example': 'still_not_project_settings'}\n",
            encoding="utf-8",
        )

        result = self.run_boundary("verify")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_unrelated_symlink_directory_is_not_traversed_for_settings(self) -> None:
        external = self.workspace / "external_data"
        external.mkdir()
        (external / "settings.py").write_text(
            "MIGRATION_MODULES = {'example': 'external_history'}\n",
            encoding="utf-8",
        )
        link = self.project / "data"
        try:
            link.symlink_to(external, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")
        spec = importlib.util.spec_from_file_location(
            "dddjango_migration_boundary_unrelated_link",
            MIGRATION_CHECK,
        )
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        with mock.patch.object(
            module,
            "_linked_python_sources",
            wraps=module._linked_python_sources,
        ) as linked_sources:
            sources = module._settings_sources(self.project)

        self.assertEqual([], sources)
        linked_sources.assert_not_called()

    def test_unregistered_nested_app_below_symlink_is_outside_static_scope(self) -> None:
        external = self.workspace / "external_packages"
        app = external / "orders"
        migrations = app / "migrations"
        migrations.mkdir(parents=True)
        (app / "__init__.py").write_text("", encoding="utf-8")
        (app / "apps.py").write_text(
            "from django.apps import AppConfig\n"
            "class OrdersConfig(AppConfig):\n"
            "    name = 'vendor.orders'\n",
            encoding="utf-8",
        )
        (app / "models.py").write_text("class Order: pass\n", encoding="utf-8")
        migration = migrations / "0001_initial.py"
        migration.write_text("operations = []\n", encoding="utf-8")
        vendor = self.project / "vendor"
        try:
            vendor.symlink_to(external, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")
        self.snapshot()

        migration.write_text("operations = ['external']\n", encoding="utf-8")
        result = self.run_boundary("verify")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_registered_external_app_target_content_is_not_tracked(self) -> None:
        external = self.workspace / "external_packages"
        app = external / "orders"
        migrations = app / "migrations"
        migrations.mkdir(parents=True)
        (app / "__init__.py").write_text("", encoding="utf-8")
        (app / "apps.py").write_text(
            "from django.apps import AppConfig\n"
            "class OrdersConfig(AppConfig):\n"
            "    name = 'vendor.orders'\n",
            encoding="utf-8",
        )
        (app / "models.py").write_text("class Order: pass\n", encoding="utf-8")
        migration = migrations / "0001_initial.py"
        migration.write_text("operations = []\n", encoding="utf-8")
        vendor = self.project / "vendor"
        try:
            vendor.symlink_to(external, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")
        (self.project / "settings.py").write_text(
            "INSTALLED_APPS = ['vendor.orders']\n",
            encoding="utf-8",
        )
        self.snapshot()

        migration.write_text("operations = ['external']\n", encoding="utf-8")

        result = self.run_boundary("verify")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_external_src_link_is_tracked_without_reading_app_target(self) -> None:
        targets: list[Path] = []
        for name in ("src_a", "src_b"):
            target = self.workspace / name
            app = target / "orders"
            migrations = app / "migrations"
            migrations.mkdir(parents=True)
            (app / "models.py").write_text(
                "class Order: pass\n",
                encoding="utf-8",
            )
            (migrations / "0001_initial.py").write_text(
                "operations = []\n",
                encoding="utf-8",
            )
            targets.append(target)
        src = self.project / "src"
        try:
            src.symlink_to(targets[0], target_is_directory=True)
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")
        (self.project / "settings.py").write_text(
            "INSTALLED_APPS = ['orders']\n",
            encoding="utf-8",
        )
        self.snapshot()

        migration = targets[0] / "orders" / "migrations" / "0001_initial.py"
        migration.write_text("operations = ['outside']\n", encoding="utf-8")
        clean = self.run_boundary("verify")
        self.assertEqual(0, clean.returncode, clean.stdout + clean.stderr)

        src.unlink()
        src.symlink_to(targets[1], target_is_directory=True)

        self.assert_boundary_blocked(".dddjango-app-directory-link/src")

    def test_aliased_os_environ_entrypoint_declares_settings(self) -> None:
        (self.project / "manage.py").write_text(
            "import os as operating_system\n\n"
            "operating_system.environ.setdefault(\n"
            "    'DJANGO_SETTINGS_MODULE', 'config.runtime'\n"
            ")\n",
            encoding="utf-8",
        )
        config = self.project / "config"
        config.mkdir()
        runtime = config / "runtime.py"
        runtime.write_text(
            "MIGRATION_MODULES = {'orders': 'history_a.orders'}\n",
            encoding="utf-8",
        )
        self.snapshot()

        runtime.write_text(
            "MIGRATION_MODULES = {'orders': 'history_b.orders'}\n",
            encoding="utf-8",
        )

        self.assert_boundary_blocked(".dddjango-migration-config/config/runtime.py")

    def test_subscript_os_environ_entrypoint_declares_settings(self) -> None:
        (self.project / "manage.py").write_text(
            "import os\n"
            "os.environ['DJANGO_SETTINGS_MODULE'] = 'config.runtime'\n",
            encoding="utf-8",
        )
        config = self.project / "config"
        config.mkdir()
        runtime = config / "runtime.py"
        runtime.write_text(
            "MIGRATION_MODULES = {'orders': 'history_a.orders'}\n",
            encoding="utf-8",
        )
        self.snapshot()

        runtime.write_text(
            "MIGRATION_MODULES = {'orders': 'history_b.orders'}\n",
            encoding="utf-8",
        )

        self.assert_boundary_blocked(".dddjango-migration-config/config/runtime.py")

    def test_imported_environ_subscript_entrypoint_declares_settings(self) -> None:
        (self.project / "manage.py").write_text(
            "from os import environ as environment\n"
            "environment['DJANGO_SETTINGS_MODULE'] = 'config.runtime'\n",
            encoding="utf-8",
        )
        config = self.project / "config"
        config.mkdir()
        runtime = config / "runtime.py"
        runtime.write_text(
            "MIGRATION_MODULES = {'orders': 'history_a.orders'}\n",
            encoding="utf-8",
        )
        self.snapshot()

        runtime.write_text(
            "MIGRATION_MODULES = {'orders': 'history_b.orders'}\n",
            encoding="utf-8",
        )

        self.assert_boundary_blocked(".dddjango-migration-config/config/runtime.py")

    def test_augmented_installed_apps_registration_is_tracked(self) -> None:
        app = self.project / "legacy"
        app.mkdir()
        (app / "__init__.py").write_text("", encoding="utf-8")
        model = app / "models.py"
        model.write_text("class Legacy: pass\n", encoding="utf-8")
        (self.project / "settings.py").write_text(
            "INSTALLED_APPS = []\n"
            "INSTALLED_APPS += ['legacy']\n",
            encoding="utf-8",
        )
        self.snapshot()

        model.unlink()

        self.assert_boundary_blocked("legacy/models.py")

    def test_dict_union_augmented_migration_modules_is_tracked(self) -> None:
        (self.project / "settings.py").write_text(
            "MIGRATION_MODULES = {}\n"
            "MIGRATION_MODULES |= {'orders': 'custom_history.orders'}\n",
            encoding="utf-8",
        )
        custom = self.project / "custom_history" / "orders"
        custom.mkdir(parents=True)
        migration = custom / "0001_initial.py"
        migration.write_text("operations = []\n", encoding="utf-8")
        self.snapshot()

        migration.write_text("operations = ['external']\n", encoding="utf-8")

        self.assert_boundary_blocked("custom_history/orders/0001_initial.py")

    def test_valid_migration_modules_becoming_invalid_is_blocked(self) -> None:
        settings = self.project / "settings.py"
        settings.write_text(
            'MIGRATION_MODULES = {"orders": "schema_history.orders"}\n',
            encoding="utf-8",
        )
        self.snapshot()

        settings.write_text("MIGRATION_MODULES = {\n", encoding="utf-8")

        result = self.run_boundary("verify")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("settings source", result.stderr)

    def test_initial_invalid_settings_fails_closed(self) -> None:
        (self.project / "settings.py").write_text(
            "MIGRATION_MODULES = {\n",
            encoding="utf-8",
        )
        custom = self.project / "schema_history" / "orders"
        custom.mkdir(parents=True)
        (custom / "0001_initial.py").write_text(
            "operations = []\n",
            encoding="utf-8",
        )

        result = self.run_boundary("preflight")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("settings source", result.stderr)

    def test_pep263_settings_registration_is_tracked(self) -> None:
        app = self.project / "venv" / "orders"
        app.mkdir(parents=True)
        (app / "models.py").write_text("class Order: pass\n", encoding="utf-8")
        migrations = app / "migrations"
        migrations.mkdir()
        migration = migrations / "0001_initial.py"
        migration.write_text("operations = []\n", encoding="utf-8")
        (self.project / "settings.py").write_bytes(
            b"# -*- coding: latin-1 -*-\n"
            b"# caf\xe9\n"
            b"INSTALLED_APPS = ['venv.orders']\n"
        )
        self.snapshot()

        migration.write_text("operations = ['changed']\n", encoding="utf-8")

        self.assert_boundary_blocked("venv/orders/migrations/0001_initial.py")

    def test_utf8_bom_settings_migration_modules_is_tracked(self) -> None:
        (self.project / "settings.py").write_bytes(
            b"\xef\xbb\xbfMIGRATION_MODULES = {'orders': 'schema_history.orders'}\n"
        )
        custom = self.project / "schema_history" / "orders"
        custom.mkdir(parents=True)
        migration = custom / "0001_initial.py"
        migration.write_text("operations = []\n", encoding="utf-8")
        self.snapshot()

        migration.write_text("operations = ['changed']\n", encoding="utf-8")

        self.assert_boundary_blocked("schema_history/orders/0001_initial.py")

    def test_current_behavior_test_with_migration_in_name_is_not_frozen(self) -> None:
        tests = self.project / "tests"
        tests.mkdir()
        behavior_test = tests / "test_account_migration_banner.py"
        behavior_test.write_text("def test_current_banner(): pass\n", encoding="utf-8")
        self.snapshot()

        behavior_test.write_text("def test_updated_banner(): pass\n", encoding="utf-8")

        result = self.run_boundary("verify")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_recovery_reports_interrupted_change_before_new_baseline(self) -> None:
        migrations = self.make_migrations()
        artifacts = self.project / ".dddjango" / "20260713-orders"
        artifacts.mkdir(parents=True)
        orphan = artifacts / "migration-boundary-epoch-20260713-120000-01.json"
        snapshot = self.run_boundary("snapshot", orphan)
        self.assertEqual(0, snapshot.returncode, snapshot.stdout + snapshot.stderr)

        (migrations / "0001_initial.py").write_text(
            "operations = ['interrupted change']\n",
            encoding="utf-8",
        )

        recovery = self.run_boundary("recover", self.project / ".dddjango")
        self.assertEqual(2, recovery.returncode, recovery.stdout + recovery.stderr)
        self.assertIn(str(orphan), recovery.stdout)
        self.assertIn("orders/migrations/0001_initial.py", recovery.stdout)

    def test_recovery_accepts_clean_orphan_epoch(self) -> None:
        self.make_migrations()
        artifacts = self.project / ".dddjango" / "20260713-orders"
        artifacts.mkdir(parents=True)
        orphan = artifacts / "migration-boundary-epoch-20260713-120000-01.json"
        snapshot = self.run_boundary("snapshot", orphan)
        self.assertEqual(0, snapshot.returncode, snapshot.stdout + snapshot.stderr)

        recovery = self.run_boundary("recover", self.project / ".dddjango")

        self.assertEqual(0, recovery.returncode, recovery.stdout + recovery.stderr)
        self.assertIn("1 orphan epoch baseline 일치", recovery.stdout)

    def test_recovery_rejects_malformed_orphan_epoch(self) -> None:
        artifacts = self.project / ".dddjango" / "20260713-orders"
        artifacts.mkdir(parents=True)
        orphan = artifacts / "migration-boundary-epoch-20260713-120000-01.json"
        orphan.write_text("{}\n", encoding="utf-8")

        recovery = self.run_boundary("recover", self.project / ".dddjango")

        self.assertEqual(1, recovery.returncode, recovery.stdout + recovery.stderr)
        self.assertIn("baseline 최상위 형식", recovery.stderr)

    def test_existing_app_identity_removal_is_blocked(self) -> None:
        app = self.make_app("legacy")
        (self.project / "settings.py").write_text(
            'INSTALLED_APPS = ["legacy"]\n',
            encoding="utf-8",
        )
        self.snapshot()

        (app / "apps.py").unlink()
        (app / "models.py").unlink()

        self.assert_boundary_blocked("legacy/apps.py")

    def test_models_only_app_identity_removal_is_blocked(self) -> None:
        app = self.project / "legacy"
        app.mkdir()
        (app / "__init__.py").write_text("", encoding="utf-8")
        model = app / "models.py"
        model.write_text("class Legacy: pass\n", encoding="utf-8")
        (self.project / "settings.py").write_text(
            'INSTALLED_APPS = ["legacy"]\n',
            encoding="utf-8",
        )
        self.snapshot()

        model.unlink()

        self.assert_boundary_blocked("legacy/models.py")

    def test_entrypoint_declared_nonstandard_settings_tracks_models_only_app(self) -> None:
        (self.project / "manage.py").write_text(
            "import os\n"
            "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_settings')\n",
            encoding="utf-8",
        )
        app = self.project / "legacy"
        app.mkdir()
        (app / "__init__.py").write_text("", encoding="utf-8")
        model = app / "models.py"
        model.write_text("class Legacy: pass\n", encoding="utf-8")
        (self.project / "project_settings.py").write_text(
            "INSTALLED_APPS = ['legacy']\n",
            encoding="utf-8",
        )
        self.snapshot()

        model.unlink()

        self.assert_boundary_blocked("legacy/models.py")

    def test_divergent_entrypoints_union_custom_migration_roots(self) -> None:
        (self.project / "manage.py").write_text(
            "import os\n"
            "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dev_settings')\n",
            encoding="utf-8",
        )
        (self.project / "asgi.py").write_text(
            "import os\n"
            "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prod_settings')\n",
            encoding="utf-8",
        )
        (self.project / "dev_settings.py").write_text(
            "INSTALLED_APPS = []\n",
            encoding="utf-8",
        )
        (self.project / "prod_settings.py").write_text(
            "INSTALLED_APPS = []\n"
            "MIGRATION_MODULES = {'orders': 'prod_migrations'}\n",
            encoding="utf-8",
        )
        custom_root = self.project / "prod_migrations"
        custom_root.mkdir()
        (custom_root / "__init__.py").write_text("", encoding="utf-8")
        migration = custom_root / "0001_initial.py"
        migration.write_text("operations = []\n", encoding="utf-8")
        self.snapshot()

        migration.write_text("operations = ['changed']\n", encoding="utf-8")

        self.assert_boundary_blocked("prod_migrations/0001_initial.py")

    def test_models_only_symlinked_app_retarget_is_blocked(self) -> None:
        targets: list[Path] = []
        for name in ("legacy_a", "legacy_b"):
            target = self.workspace / name
            target.mkdir()
            (target / "models.py").write_text("class Legacy: pass\n", encoding="utf-8")
            targets.append(target)
        link = self.project / "legacy"
        try:
            link.symlink_to(targets[0], target_is_directory=True)
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")
        (self.project / "settings.py").write_text(
            'INSTALLED_APPS = ["legacy"]\n',
            encoding="utf-8",
        )
        self.snapshot()

        link.unlink()
        link.symlink_to(targets[1], target_is_directory=True)

        self.assert_boundary_blocked(
            ".dddjango-app-directory-link/legacy"
        )

    def test_registered_app_symlink_ancestor_retarget_is_blocked(self) -> None:
        targets: list[Path] = []
        for name in ("vendor_a", "vendor_b"):
            target = self.workspace / name
            app = target / "legacy"
            app.mkdir(parents=True)
            (app / "models.py").write_text(
                "class Legacy: pass\n",
                encoding="utf-8",
            )
            (app / "config.py").write_text(
                "from django.apps import AppConfig\n"
                "class LegacyConfig(AppConfig):\n"
                "    name = 'vendor.legacy'\n",
                encoding="utf-8",
            )
            targets.append(target)
        vendor = self.project / "vendor"
        try:
            vendor.symlink_to(targets[0], target_is_directory=True)
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")
        (self.project / "settings.py").write_text(
            "INSTALLED_APPS = ['vendor.legacy.config.LegacyConfig']\n",
            encoding="utf-8",
        )
        self.snapshot()

        vendor.unlink()
        vendor.symlink_to(targets[1], target_is_directory=True)

        self.assert_boundary_blocked(".dddjango-app-directory-link/vendor")

    def test_external_intermediate_target_retarget_is_not_tracked(self) -> None:
        targets: list[Path] = []
        for name in ("app_a", "app_b"):
            target = self.workspace / name
            target.mkdir()
            (target / "models.py").write_text(
                "class Legacy: pass\n",
                encoding="utf-8",
            )
            migrations = target / "migrations"
            migrations.mkdir()
            (migrations / "0001_initial.py").write_text(
                "operations = []\n",
                encoding="utf-8",
            )
            targets.append(target)
        alias = self.workspace / "alias"
        linked_app = self.project / "linked_app"
        try:
            alias.symlink_to(targets[0], target_is_directory=True)
            linked_app.symlink_to(alias, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")
        (self.project / "settings.py").write_text(
            "INSTALLED_APPS = ['linked_app']\n",
            encoding="utf-8",
        )
        self.snapshot()

        alias.unlink()
        alias.symlink_to(targets[1], target_is_directory=True)

        result = self.run_boundary("verify")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_external_settings_registration_content_is_not_read(self) -> None:
        self.declare_settings_module("config.settings")
        self.make_app("legacy")
        external = self.workspace / "settings_package"
        external.mkdir()
        settings = external / "settings.py"
        settings.write_text('INSTALLED_APPS = ["legacy"]\n', encoding="utf-8")
        link = self.project / "config"
        try:
            link.symlink_to(external, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")
        self.snapshot()

        settings.write_text('INSTALLED_APPS = ["copied_legacy"]\n', encoding="utf-8")

        result = self.run_boundary("verify")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_existing_app_config_name_change_is_blocked(self) -> None:
        app = self.make_app("legacy")
        app_config = app / "apps.py"
        app_config.write_text(
            "from django.apps import AppConfig\n"
            "class LegacyConfig(AppConfig):\n"
            '    name = "legacy"\n'
            '    label = "legacy"\n',
            encoding="utf-8",
        )
        self.snapshot()

        app_config.write_text(
            "from django.apps import AppConfig\n"
            "class LegacyConfig(AppConfig):\n"
            '    name = "copied_legacy"\n'
            '    label = "copied_legacy"\n',
            encoding="utf-8",
        )

        self.assert_boundary_blocked(".dddjango-app-config/legacy/apps.py")

    def test_app_config_name_label_reordering_is_not_a_boundary_change(self) -> None:
        app = self.make_app("legacy")
        app_config = app / "apps.py"
        app_config.write_text(
            "from django.apps import AppConfig\n"
            "class LegacyConfig(AppConfig):\n"
            "    name = 'legacy'\n"
            "    label = 'legacy_label'\n",
            encoding="utf-8",
        )
        self.snapshot()

        app_config.write_text(
            "from django.apps import AppConfig\n"
            "class LegacyConfig(AppConfig):\n"
            "    label = 'legacy_label'\n"
            "    name = 'legacy'\n",
            encoding="utf-8",
        )

        result = self.run_boundary("verify")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_aliased_app_config_name_change_is_blocked(self) -> None:
        app = self.make_app("legacy")
        app_config = app / "apps.py"
        app_config.write_text(
            "from django.apps import AppConfig as DjangoConfig\n"
            "class LegacyConfig(DjangoConfig):\n"
            "    name = 'legacy'\n"
            "    label = 'legacy'\n",
            encoding="utf-8",
        )
        self.snapshot()

        app_config.write_text(
            "from django.apps import AppConfig as DjangoConfig\n"
            "class LegacyConfig(DjangoConfig):\n"
            "    name = 'copied_legacy'\n"
            "    label = 'copied_legacy'\n",
            encoding="utf-8",
        )

        self.assert_boundary_blocked(".dddjango-app-config/legacy/apps.py")

    def test_try_imported_app_config_migration_change_is_blocked(self) -> None:
        app = self.make_app("orders")
        (app / "apps.py").write_text(
            "try:\n"
            "    from django.apps import AppConfig\n"
            "except ImportError:\n"
            "    raise\n\n"
            "class OrdersConfig(AppConfig):\n"
            "    name = 'orders'\n",
            encoding="utf-8",
        )
        migrations = app / "migrations"
        migrations.mkdir()
        migration = migrations / "0001_initial.py"
        migration.write_text("operations = []\n", encoding="utf-8")
        self.snapshot()

        migration.write_text("operations = ['changed']\n", encoding="utf-8")

        self.assert_boundary_blocked("orders/migrations/0001_initial.py")

    def test_unimported_local_app_config_name_is_not_django_app_config(self) -> None:
        app = self.make_app("legacy")
        app_config = app / "apps.py"
        app_config.write_text(
            "class AppConfig:\n"
            "    pass\n\n"
            "class LocalConfig(AppConfig):\n"
            "    name = 'legacy'\n",
            encoding="utf-8",
        )
        self.snapshot()

        app_config.write_text(
            "class AppConfig:\n"
            "    pass\n\n"
            "class LocalConfig(AppConfig):\n"
            "    name = 'current'\n",
            encoding="utf-8",
        )

        result = self.run_boundary("verify")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_registered_nonstandard_app_config_module_change_is_blocked(self) -> None:
        app = self.project / "legacy"
        app.mkdir()
        (app / "__init__.py").write_text("", encoding="utf-8")
        (app / "models.py").write_text("class Legacy: pass\n", encoding="utf-8")
        config = app / "config.py"
        config.write_text(
            "from django.apps import AppConfig\n"
            "class LegacyConfig(AppConfig):\n"
            "    name = 'legacy'\n"
            "    label = 'legacy'\n",
            encoding="utf-8",
        )
        (self.project / "settings.py").write_text(
            "INSTALLED_APPS = ['legacy.config.LegacyConfig']\n",
            encoding="utf-8",
        )
        self.snapshot()

        config.write_text(
            "from django.apps import AppConfig\n"
            "class LegacyConfig(AppConfig):\n"
            "    name = 'copied_legacy'\n"
            "    label = 'copied_legacy'\n",
            encoding="utf-8",
        )

        self.assert_boundary_blocked(".dddjango-app-config/legacy/config.py")

    def test_local_app_config_subclass_field_change_is_blocked(self) -> None:
        app = self.project / "legacy"
        app.mkdir()
        (app / "__init__.py").write_text("", encoding="utf-8")
        (app / "models.py").write_text("class Legacy: pass\n", encoding="utf-8")
        config = app / "apps.py"
        config.write_text(
            "from django.apps import AppConfig\n"
            "class BaseConfig(AppConfig):\n"
            "    name = 'legacy'\n"
            "class LegacyConfig(BaseConfig):\n"
            "    label = 'legacy'\n",
            encoding="utf-8",
        )
        (self.project / "settings.py").write_text(
            "INSTALLED_APPS = ['legacy.apps.LegacyConfig']\n",
            encoding="utf-8",
        )
        self.snapshot()

        config.write_text(
            "from django.apps import AppConfig\n"
            "class BaseConfig(AppConfig):\n"
            "    name = 'legacy'\n"
            "class LegacyConfig(BaseConfig):\n"
            "    label = 'copied_legacy'\n",
            encoding="utf-8",
        )

        self.assert_boundary_blocked(".dddjango-app-config/legacy/apps.py")

    def test_unrelated_qualified_base_config_is_not_local_subclass(self) -> None:
        app = self.make_app("legacy")
        config = app / "apps.py"
        config.write_text(
            "from django.apps import AppConfig\n"
            "class BaseConfig(AppConfig):\n"
            "    name = 'legacy'\n"
            "class Helper(external.BaseConfig):\n"
            "    label = 'old_helper'\n",
            encoding="utf-8",
        )
        self.snapshot()

        config.write_text(
            "from django.apps import AppConfig\n"
            "class BaseConfig(AppConfig):\n"
            "    name = 'legacy'\n"
            "class Helper(external.BaseConfig):\n"
            "    label = 'current_helper'\n",
            encoding="utf-8",
        )

        result = self.run_boundary("verify")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_registered_cross_module_app_config_field_change_is_blocked(self) -> None:
        (self.project / "common.py").write_text(
            "from django.apps import AppConfig\n"
            "class BaseConfig(AppConfig):\n"
            "    pass\n",
            encoding="utf-8",
        )
        app = self.project / "legacy"
        app.mkdir()
        (app / "__init__.py").write_text("", encoding="utf-8")
        (app / "models.py").write_text("class Legacy: pass\n", encoding="utf-8")
        config = app / "config.py"
        config.write_text(
            "from common import BaseConfig\n"
            "class LegacyConfig(BaseConfig):\n"
            "    name = 'legacy'\n"
            "    label = 'legacy'\n",
            encoding="utf-8",
        )
        (self.project / "settings.py").write_text(
            "INSTALLED_APPS = ['legacy.config.LegacyConfig']\n",
            encoding="utf-8",
        )
        self.snapshot()

        config.write_text(
            "from common import BaseConfig\n"
            "class LegacyConfig(BaseConfig):\n"
            "    name = 'legacy'\n"
            "    label = 'copied_legacy'\n",
            encoding="utf-8",
        )

        self.assert_boundary_blocked(".dddjango-app-config/legacy/config.py")

    def test_adding_app_config_to_existing_registered_app_is_blocked(self) -> None:
        app = self.project / "legacy"
        app.mkdir()
        (app / "__init__.py").write_text("", encoding="utf-8")
        (app / "models.py").write_text("class Legacy: pass\n", encoding="utf-8")
        (app / "apps.py").write_text("VALUE = 1\n", encoding="utf-8")
        (self.project / "settings.py").write_text(
            'INSTALLED_APPS = ["legacy"]\n',
            encoding="utf-8",
        )
        self.snapshot()

        (app / "apps.py").write_text(
            "from django.apps import AppConfig\n"
            "class CopiedLegacyConfig(AppConfig):\n"
            '    name = "copied_legacy"\n',
            encoding="utf-8",
        )

        self.assert_boundary_blocked(".dddjango-app-config/legacy/apps.py")

    def test_unrelated_models_module_is_not_treated_as_django_app(self) -> None:
        tests = self.project / "tests"
        tests.mkdir()
        models = tests / "models.py"
        models.write_text("VALUE = 1\n", encoding="utf-8")
        self.snapshot()

        models.unlink()

        result = self.run_boundary("verify")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_nonlocal_installed_app_is_not_frozen(self) -> None:
        settings = self.project / "settings.py"
        settings.write_text(
            'INSTALLED_APPS = ["debug_toolbar"]\n',
            encoding="utf-8",
        )
        self.snapshot()

        settings.write_text("INSTALLED_APPS = []\n", encoding="utf-8")

        result = self.run_boundary("verify")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_registered_package_without_django_markers_is_not_an_error(self) -> None:
        package = self.project / "project" / "feature"
        package.mkdir(parents=True)
        (package / "__init__.py").write_text("", encoding="utf-8")
        (self.project / "settings.py").write_text(
            'INSTALLED_APPS = ["project.feature"]\n',
            encoding="utf-8",
        )

        self.snapshot()

    def test_existing_static_app_registration_replacement_is_blocked(self) -> None:
        settings = self.project / "settings.py"
        settings.write_text('INSTALLED_APPS = ["legacy"]\n', encoding="utf-8")
        self.make_app("legacy")
        self.snapshot()

        settings.write_text('INSTALLED_APPS = ["copied_legacy"]\n', encoding="utf-8")

        self.assert_boundary_blocked("settings.py::legacy")

    def test_new_app_config_and_registration_are_allowed(self) -> None:
        settings = self.project / "settings.py"
        settings.write_text('INSTALLED_APPS = ["legacy"]\n', encoding="utf-8")
        self.make_app("legacy")
        self.snapshot()

        app = self.make_app("orders")
        (app / "apps.py").write_text(
            "from django.apps import AppConfig\n"
            "class OrdersConfig(AppConfig):\n"
            '    name = "orders"\n',
            encoding="utf-8",
        )
        settings.write_text(
            'INSTALLED_APPS = ["legacy", "orders"]\n',
            encoding="utf-8",
        )

        result = self.run_boundary("verify")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_new_nested_app_config_is_allowed(self) -> None:
        self.make_app("orders")
        self.snapshot()

        audit = self.project / "orders" / "audit"
        audit.mkdir()
        (audit / "apps.py").write_text(
            "from django.apps import AppConfig\n"
            "class AuditConfig(AppConfig):\n"
            "    name = 'orders.audit'\n",
            encoding="utf-8",
        )
        (audit / "models.py").write_text("class AuditRecord: pass\n", encoding="utf-8")

        result = self.run_boundary("verify")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_g0_state_applies_default_location_without_root_app_convention(self) -> None:
        self.snapshot()
        (self.project / "application").mkdir()
        self.make_app("cache")

        result = subprocess.run(
            [sys.executable, str(LAYER_CHECK), str(self.project), str(self.state)],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("cache", result.stdout)

    def test_layer_check_does_not_guess_non_django_models_package_as_app(self) -> None:
        (self.project / "application").mkdir()
        self.snapshot()
        analytics = self.project / "analytics"
        analytics.mkdir()
        (analytics / "__init__.py").write_text("", encoding="utf-8")
        (analytics / "models.py").write_text(
            "from dataclasses import dataclass\n\n@dataclass\nclass Report:\n    value: int\n",
            encoding="utf-8",
        )

        result = subprocess.run(
            [sys.executable, str(LAYER_CHECK), str(self.project), str(self.state)],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_layer_check_preserves_nonstandard_root_app_project_convention(self) -> None:
        self.make_app("legacy")
        (self.project / "settings.py").write_text(
            'INSTALLED_APPS = ["legacy"]\n',
            encoding="utf-8",
        )
        self.snapshot()
        self.make_app("orders")

        result = subprocess.run(
            [sys.executable, str(LAYER_CHECK), str(self.project), str(self.state)],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_layer_check_prefers_existing_standard_container_in_mixed_project(self) -> None:
        self.make_app("legacy")
        (self.project / "application").mkdir()
        (self.project / "settings.py").write_text(
            'INSTALLED_APPS = ["legacy"]\n',
            encoding="utf-8",
        )
        self.snapshot()
        self.make_app("orders")

        result = subprocess.run(
            [sys.executable, str(LAYER_CHECK), str(self.project), str(self.state)],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("orders", result.stdout)

    def test_layer_check_remembers_removed_standard_container_from_g0(self) -> None:
        self.make_app("legacy")
        application = self.project / "application"
        application.mkdir()
        (application / "__init__.py").write_text("", encoding="utf-8")
        (self.project / "settings.py").write_text(
            'INSTALLED_APPS = ["legacy"]\n',
            encoding="utf-8",
        )
        self.snapshot()
        (application / "__init__.py").unlink()
        application.rmdir()
        self.make_app("orders")

        result = subprocess.run(
            [sys.executable, str(LAYER_CHECK), str(self.project), str(self.state)],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("orders", result.stdout)

    def test_layer_check_detects_root_app_config_imported_from_django(self) -> None:
        self.snapshot()
        app = self.project / "orders"
        app.mkdir()
        (app / "__init__.py").write_text("", encoding="utf-8")
        (app / "apps.py").write_text(
            "from django import apps\n"
            "class OrdersConfig(apps.AppConfig):\n"
            "    name = 'orders'\n",
            encoding="utf-8",
        )

        result = subprocess.run(
            [sys.executable, str(LAYER_CHECK), str(self.project), str(self.state)],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("orders", result.stdout)

    def test_layer_check_detects_namespace_root_app_without_init(self) -> None:
        self.snapshot()
        app = self.project / "orders"
        app.mkdir()
        (app / "apps.py").write_text(
            "from django.apps import AppConfig\n"
            "class OrdersConfig(AppConfig):\n"
            "    name = 'orders'\n",
            encoding="utf-8",
        )

        result = subprocess.run(
            [sys.executable, str(LAYER_CHECK), str(self.project), str(self.state)],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("orders", result.stdout)

    def test_layer_check_detects_root_app_config_via_django_module(self) -> None:
        self.snapshot()
        app = self.project / "orders"
        app.mkdir()
        (app / "__init__.py").write_text("", encoding="utf-8")
        (app / "apps.py").write_text(
            "import django\n"
            "class OrdersConfig(django.apps.AppConfig):\n"
            "    name = 'orders'\n",
            encoding="utf-8",
        )

        result = subprocess.run(
            [sys.executable, str(LAYER_CHECK), str(self.project), str(self.state)],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("orders", result.stdout)

    def test_layer_check_detects_models_only_root_django_app(self) -> None:
        self.snapshot()
        app = self.project / "orders"
        app.mkdir()
        (app / "__init__.py").write_text("", encoding="utf-8")
        (app / "models.py").write_text(
            "from django.db import models\n"
            "class Order(models.Model):\n"
            "    pass\n",
            encoding="utf-8",
        )

        result = subprocess.run(
            [sys.executable, str(LAYER_CHECK), str(self.project), str(self.state)],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("orders", result.stdout)

    def test_layer_check_ignores_flat_app_migration_only_change(self) -> None:
        bc = self.project / "application" / "orders"
        bc.mkdir(parents=True)
        (bc / "__init__.py").write_text("", encoding="utf-8")
        (bc / "models.py").write_text(
            "from django.db import models\n"
            "class Order(models.Model):\n"
            "    pass\n",
            encoding="utf-8",
        )
        migrations = bc / "migrations"
        migrations.mkdir()
        (migrations / "__init__.py").write_text("", encoding="utf-8")
        migration = migrations / "0001_initial.py"
        migration.write_text("operations = []\n", encoding="utf-8")
        (self.project / "settings.py").write_text(
            "INSTALLED_APPS = ['application.orders']\n",
            encoding="utf-8",
        )
        self.snapshot()
        self.commit_project_baseline()

        migration.write_text("operations = ['external']\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(LAYER_CHECK), str(self.project), str(self.state)],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_layer_check_ignores_custom_migration_root_only_change(self) -> None:
        bc = self.project / "application" / "orders"
        bc.mkdir(parents=True)
        (bc / "__init__.py").write_text("", encoding="utf-8")
        (bc / "models.py").write_text(
            "from django.db import models\n"
            "class Order(models.Model):\n"
            "    pass\n",
            encoding="utf-8",
        )
        history = bc / "schema_history"
        history.mkdir()
        (history / "__init__.py").write_text("", encoding="utf-8")
        migration = history / "0001_initial.py"
        migration.write_text("operations = []\n", encoding="utf-8")
        (self.project / "settings.py").write_text(
            "INSTALLED_APPS = ['application.orders']\n"
            "MIGRATION_MODULES = {'orders': 'application.orders.schema_history'}\n",
            encoding="utf-8",
        )
        self.snapshot()
        self.commit_project_baseline()

        migration.write_text("operations = ['external']\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(LAYER_CHECK), str(self.project), str(self.state)],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_pipeline_boundary_pauses_before_layer_on_migration_rename(self) -> None:
        bc = self.project / "application" / "orders"
        bc.mkdir(parents=True)
        (bc / "__init__.py").write_text("", encoding="utf-8")
        (bc / "models.py").write_text(
            "from django.db import models\n"
            "class Order(models.Model):\n"
            "    pass\n",
            encoding="utf-8",
        )
        migrations = bc / "migrations"
        migrations.mkdir()
        (migrations / "__init__.py").write_text("", encoding="utf-8")
        migration = migrations / "0001_initial.py"
        migration.write_text("operations = []\n", encoding="utf-8")
        (self.project / "settings.py").write_text(
            "INSTALLED_APPS = ['application.orders']\n",
            encoding="utf-8",
        )
        self.snapshot()
        self.commit_project_baseline()

        migration.rename(bc / "archived_0001.py")
        boundary_result = self.run_boundary("verify")

        self.assertEqual(
            2,
            boundary_result.returncode,
            boundary_result.stdout + boundary_result.stderr,
        )
        self.assertIn("application/orders/migrations/0001_initial.py", boundary_result.stdout)

    def test_existing_flat_persistence_app_edit_is_grandfathered(self) -> None:
        bc = self.project / "application" / "orders"
        bc.mkdir(parents=True)
        (bc / "__init__.py").write_text("", encoding="utf-8")
        (bc / "models.py").write_text(
            "from django.db import models\n"
            "class Order(models.Model):\n"
            "    pass\n",
            encoding="utf-8",
        )
        migrations = bc / "migrations"
        migrations.mkdir()
        (migrations / "__init__.py").write_text("", encoding="utf-8")
        migration = migrations / "0001_initial.py"
        migration.write_text("operations = []\n", encoding="utf-8")
        (self.project / "settings.py").write_text(
            "INSTALLED_APPS = ['application.orders']\n",
            encoding="utf-8",
        )
        self.commit_project_baseline()
        migration.write_text("operations = ['preexisting dirty']\n", encoding="utf-8")
        self.snapshot()

        (bc / "service.py").write_text("VALUE = 'plugin edit'\n", encoding="utf-8")
        layer_result = subprocess.run(
            [sys.executable, str(LAYER_CHECK), str(self.project), str(self.state)],
            capture_output=True,
            text=True,
            check=False,
        )
        boundary_result = self.run_boundary("verify")

        self.assertEqual(0, layer_result.returncode, layer_result.stdout + layer_result.stderr)
        self.assertEqual(
            0,
            boundary_result.returncode,
            boundary_result.stdout + boundary_result.stderr,
        )

    def test_existing_flat_persistence_app_partial_layer_is_blocked(self) -> None:
        bc = self.project / "application" / "orders"
        bc.mkdir(parents=True)
        (bc / "__init__.py").write_text("", encoding="utf-8")
        (bc / "models.py").write_text(
            "from django.db import models\n"
            "class Order(models.Model):\n"
            "    pass\n",
            encoding="utf-8",
        )
        (self.project / "settings.py").write_text(
            "INSTALLED_APPS = ['application.orders']\n",
            encoding="utf-8",
        )
        self.snapshot()

        domain = bc / "domain_layer"
        domain.mkdir()
        (domain / "__init__.py").write_text("", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(LAYER_CHECK), str(self.project), str(self.state)],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("application/orders", result.stdout)

    def test_existing_partial_persistence_app_is_grandfathered(self) -> None:
        bc = self.project / "application" / "orders"
        domain = bc / "domain_layer"
        domain.mkdir(parents=True)
        (domain / "__init__.py").write_text("", encoding="utf-8")
        (bc / "models.py").write_text(
            "from django.db import models\n"
            "class Order(models.Model):\n"
            "    pass\n",
            encoding="utf-8",
        )
        (bc / "service.py").write_text("VALUE = 'before'\n", encoding="utf-8")
        (self.project / "settings.py").write_text(
            "INSTALLED_APPS = ['application.orders']\n",
            encoding="utf-8",
        )
        self.snapshot()
        self.commit_project_baseline()

        (bc / "service.py").write_text("VALUE = 'current'\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(LAYER_CHECK), str(self.project), str(self.state)],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_existing_nested_infra_app_partial_layers_are_grandfathered(self) -> None:
        bc = self.project / "application" / "orders"
        domain = bc / "domain_layer"
        domain.mkdir(parents=True)
        (domain / "__init__.py").write_text("", encoding="utf-8")
        django_app = bc / "infra_layer" / "django_orders"
        django_app.mkdir(parents=True)
        (django_app / "__init__.py").write_text("", encoding="utf-8")
        (django_app / "apps.py").write_text(
            "from django.apps import AppConfig\n"
            "class OrdersConfig(AppConfig):\n"
            "    name = 'application.orders.infra_layer.django_orders'\n",
            encoding="utf-8",
        )
        (django_app / "models.py").write_text(
            "from django.db import models\n"
            "class Order(models.Model):\n"
            "    pass\n",
            encoding="utf-8",
        )
        service = bc / "service.py"
        service.write_text("VALUE = 'before'\n", encoding="utf-8")
        (self.project / "settings.py").write_text(
            "INSTALLED_APPS = ["
            "'application.orders.infra_layer.django_orders.apps.OrdersConfig'"
            "]\n",
            encoding="utf-8",
        )
        self.snapshot()
        self.commit_project_baseline()

        service.write_text("VALUE = 'current'\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(LAYER_CHECK), str(self.project), str(self.state)],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_layer_check_rejects_tampered_g0_structural_baseline(self) -> None:
        bc = self.project / "application" / "orders"
        bc.mkdir(parents=True)
        (bc / "models.py").write_text(
            "from django.db import models\n"
            "class Order(models.Model):\n"
            "    pass\n",
            encoding="utf-8",
        )
        self.snapshot()
        manifest = json.loads(self.state.read_text(encoding="utf-8"))
        manifest["application_layer_issues"]["application/orders"].append(
            "tampered issue"
        )
        self.state.write_text(
            json.dumps(manifest, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        result = subprocess.run(
            [sys.executable, str(LAYER_CHECK), str(self.project), str(self.state)],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("receipt", result.stderr)

    def test_existing_complete_app_required_init_deletion_is_blocked(self) -> None:
        bc = self.make_complete_flat_persistence_bc()
        self.snapshot()
        self.commit_project_baseline()

        (bc / "presentation_layer" / "__init__.py").unlink()
        result = subprocess.run(
            [sys.executable, str(LAYER_CHECK), str(self.project), str(self.state)],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("presentation_layer/ 에 __init__.py 없음", result.stdout)

    def test_existing_complete_app_new_foreign_port_is_blocked(self) -> None:
        bc = self.make_complete_flat_persistence_bc()
        self.snapshot()
        self.commit_project_baseline()

        port = bc / "application_layer" / "place_order" / "port"
        port.mkdir(parents=True)
        (port / "inventory.py").write_text("class InventoryPort: pass\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(LAYER_CHECK), str(self.project), str(self.state)],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("application_layer/place_order/port", result.stdout)

    def test_new_flat_persistence_app_inside_standard_container_is_blocked(self) -> None:
        (self.project / "application").mkdir()
        self.snapshot()
        bc = self.project / "application" / "orders"
        bc.mkdir()
        (bc / "models.py").write_text(
            "from django.db import models\n"
            "class Order(models.Model):\n"
            "    pass\n",
            encoding="utf-8",
        )

        result = subprocess.run(
            [sys.executable, str(LAYER_CHECK), str(self.project), str(self.state)],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("application/orders", result.stdout)

    def test_application_container_search_ignores_ancestor_path_name(self) -> None:
        nested_root = self.workspace / "application" / "project"
        nested_root.mkdir(parents=True)
        spec = importlib.util.spec_from_file_location(
            "dddjango_layer_skeleton_ancestor_path",
            LAYER_CHECK,
        )
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        self.assertEqual([], module._find_application_containers(nested_root))

    def test_domain_folder_named_migrations_is_still_a_touched_bc(self) -> None:
        bc = self.project / "application" / "orders"
        domain = bc / "domain_layer"
        domain.mkdir(parents=True)
        (domain / "__init__.py").write_text("", encoding="utf-8")
        self.snapshot()
        initialized = subprocess.run(
            ["git", "init", "-q"],
            cwd=self.project,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, initialized.returncode, initialized.stderr)
        added = subprocess.run(
            ["git", "add", "."],
            cwd=self.project,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, added.returncode, added.stderr)
        committed = subprocess.run(
            [
                "git",
                "-c",
                "user.name=dddjango-test",
                "-c",
                "user.email=dddjango@example.invalid",
                "commit",
                "-q",
                "-m",
                "baseline",
            ],
            cwd=self.project,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, committed.returncode, committed.stderr)
        feature = domain / "migrations"
        feature.mkdir()
        (feature / "rule.py").write_text("RULE = 'current'\n", encoding="utf-8")

        result = subprocess.run(
            [sys.executable, str(LAYER_CHECK), str(self.project), str(self.state)],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("application/orders", result.stdout)

    def test_snapshot_is_write_once_for_one_epoch_file(self) -> None:
        self.snapshot()

        result = self.run_boundary("snapshot")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("재기준화를 거부", result.stderr)

    def test_snapshot_state_inside_custom_migration_root_is_rejected(self) -> None:
        custom = self.project / "schema_history" / "orders"
        custom.mkdir(parents=True)
        (self.project / "settings.py").write_text(
            "MIGRATION_MODULES = {'orders': 'schema_history.orders'}\n",
            encoding="utf-8",
        )
        state = custom / "epoch.json"

        result = self.run_boundary("snapshot", state)

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("opaque-owned path 밖", result.stderr)
        self.assertFalse(state.exists())
        self.assertFalse(state.with_name("epoch.json.write-once").exists())

    def test_external_owned_file_is_opaque_hashed_and_change_is_blocked(self) -> None:
        lifecycle_test = self.project / "qa" / "migration_test.py"
        lifecycle_test.parent.mkdir()
        lifecycle_test.write_bytes(b"\xff\xfeexternal lifecycle bytes\n")

        snapshot = self.run_boundary(
            "snapshot",
            external_owned_opaque_paths=["qa/migration_test.py"],
        )
        self.assertEqual(0, snapshot.returncode, snapshot.stdout + snapshot.stderr)
        manifest = json.loads(self.state.read_text(encoding="utf-8"))
        self.assertEqual(
            ["qa/migration_test.py"],
            manifest["external_owned_opaque_paths"],
        )
        self.assertTrue(
            any(
                entry["path"]
                == ".dddjango-external-owned-opaque/qa/migration_test.py"
                for entry in manifest["entries"]
            )
        )

        lifecycle_test.write_bytes(b"changed without semantic parsing\n")
        verify = self.run_boundary("verify")

        self.assertEqual(2, verify.returncode, verify.stdout + verify.stderr)
        self.assertIn(
            ".dddjango-external-owned-opaque/qa/migration_test.py",
            verify.stdout,
        )

    def test_external_owned_scope_rejects_dot_directory_and_symlink_ancestor(self) -> None:
        directory = self.project / "qa"
        directory.mkdir()
        dot = self.run_boundary("snapshot", external_owned_opaque_paths=["."])
        self.assertEqual(1, dot.returncode, dot.stdout + dot.stderr)

        directory_result = self.run_boundary(
            "snapshot",
            external_owned_opaque_paths=["qa"],
        )
        self.assertEqual(
            1,
            directory_result.returncode,
            directory_result.stdout + directory_result.stderr,
        )
        self.assertIn("exact file", directory_result.stderr)

        external = self.workspace / "external-tests"
        external.mkdir()
        (external / "migration_test.py").write_text("pass\n", encoding="utf-8")
        linked = self.project / "linked-tests"
        try:
            linked.symlink_to(external, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")
        linked_result = self.run_boundary(
            "snapshot",
            external_owned_opaque_paths=["linked-tests/migration_test.py"],
        )
        self.assertEqual(
            1,
            linked_result.returncode,
            linked_result.stdout + linked_result.stderr,
        )
        self.assertIn("조상에는 symlink", linked_result.stderr)

    def test_external_owned_scope_cannot_hide_structural_settings_source(self) -> None:
        (self.project / "settings.py").write_text(
            "MIGRATION_MODULES = {'orders': 'schema_history.orders'}\n",
            encoding="utf-8",
        )

        result = self.run_boundary(
            "snapshot",
            external_owned_opaque_paths=["settings.py"],
        )

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("structural discovery source", result.stderr)

    def test_nested_migration_symlink_target_is_recorded_for_general_checks(self) -> None:
        app = self.make_app("orders")
        migrations = app / "migrations"
        migrations.mkdir()
        (migrations / "__init__.py").write_text("", encoding="utf-8")
        target = self.project / "shared" / "history"
        target.mkdir(parents=True)
        (target / "handler.py").write_text(
            "@api.exception_handler(ValueError)\n"
            "def handle_value_error(request, exc):\n"
            "    return None\n",
            encoding="utf-8",
        )
        file_target = self.project / "shared" / "ops.py"
        file_target.write_text(
            "@api.exception_handler(TypeError)\n"
            "def handle_type_error(request, exc):\n"
            "    return None\n",
            encoding="utf-8",
        )
        try:
            (migrations / "legacy").symlink_to(target, target_is_directory=True)
            (migrations / "legacy_handler.py").symlink_to(file_target)
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")

        self.snapshot()
        manifest = json.loads(self.state.read_text(encoding="utf-8"))
        self.assertIn("shared/history", manifest["migration_alias_targets"])
        self.assertIn("shared/ops.py", manifest["migration_alias_targets"])
        environment = os.environ.copy()
        environment["DDDJANGO_G0_BOUNDARY_STATE"] = str(self.state)
        result = subprocess.run(
            [
                sys.executable,
                str(
                    REPO_ROOT
                    / "dddjango"
                    / "scripts"
                    / "check-catch-all-handler.py"
                ),
                str(self.project),
            ],
            capture_output=True,
            text=True,
            check=False,
            env=environment,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_snapshot_rejects_state_inside_migration_alias_target(self) -> None:
        app = self.make_app("orders")
        target = self.project / "shared" / "history"
        target.mkdir(parents=True)
        try:
            (app / "migrations").symlink_to(target, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")
        state = target / "migration-boundary-epoch-alias.json"

        result = self.run_boundary("snapshot", state)

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("opaque-owned path 밖", result.stderr)
        self.assertFalse(state.exists())

    def test_preflight_rejects_artifact_path_inside_alias_without_writing(self) -> None:
        app = self.make_app("orders")
        target = self.project / ".dddjango"
        target.mkdir()
        lock = target / "migration-boundary-coordinator.lock"
        lock.mkdir()
        try:
            (app / "migrations").symlink_to(target, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")
        state = target / "migration-boundary-epoch-preflight.json"

        result = self.run_boundary("preflight", state)

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("opaque-owned path 밖", result.stderr)
        self.assertTrue(lock.is_dir())
        self.assertFalse(state.exists())
        self.assertFalse(state.with_name(f"{state.name}.write-once").exists())

    def test_dangling_migration_alias_cannot_be_realized_by_artifact_write(self) -> None:
        app = self.make_app("orders")
        artifact_root = self.project / ".dddjango"
        self.assertFalse(artifact_root.exists())
        try:
            (app / "migrations").symlink_to(
                artifact_root,
                target_is_directory=True,
            )
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")
        state = artifact_root / "migration-boundary-epoch-dangling.json"

        preflight = self.run_boundary("preflight", state)
        snapshot = self.run_boundary("snapshot", state)

        self.assertEqual(1, preflight.returncode, preflight.stdout + preflight.stderr)
        self.assertEqual(1, snapshot.returncode, snapshot.stdout + snapshot.stderr)
        self.assertIn("opaque-owned path 밖", preflight.stderr)
        self.assertIn("opaque-owned path 밖", snapshot.stderr)
        self.assertFalse(artifact_root.exists())

    def test_dangling_receipt_alias_is_rejected_before_pair_write(self) -> None:
        app = self.make_app("orders")
        migrations = app / "migrations"
        migrations.mkdir()
        artifact_root = self.project / ".dddjango" / "feature"
        state = artifact_root / "migration-boundary-epoch-receipt.json"
        receipt = state.with_name(f"{state.name}.write-once")
        try:
            (migrations / "receipt-alias").symlink_to(receipt)
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")

        result = self.run_boundary("snapshot", state)

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("opaque-owned path 밖", result.stderr)
        self.assertFalse(self.project.joinpath(".dddjango").exists())

    def test_recovery_rejects_owned_epoch_descendant_before_reading_it(self) -> None:
        app = self.make_app("orders")
        migrations = app / "migrations"
        migrations.mkdir()
        artifacts = self.project / ".dddjango"
        artifacts.mkdir()
        trap = artifacts / "migration-boundary-epoch-trap.json"
        os.mkfifo(trap)
        try:
            (migrations / "epoch-alias").symlink_to(trap)
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")

        result = self.run_boundary("recover", artifacts)

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("current opaque-owned path 밖", result.stderr)

    def test_lock_path_requires_its_own_preflight(self) -> None:
        app = self.make_app("orders")
        migrations = app / "migrations"
        migrations.mkdir()
        lock = self.project / ".dddjango" / "migration-boundary-coordinator.lock"
        planned_state = (
            self.project
            / ".dddjango"
            / "feature"
            / "migration-boundary-epoch-planned.json"
        )
        try:
            (migrations / "lock-alias").symlink_to(
                lock,
                target_is_directory=True,
            )
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")

        state_preflight = self.run_boundary("preflight", planned_state)
        lock_preflight = self.run_boundary("preflight", lock)
        root_preflight = self.run_boundary("preflight", self.project / ".dddjango")
        snapshot = self.run_boundary("snapshot", planned_state)

        self.assertEqual(
            0,
            state_preflight.returncode,
            state_preflight.stdout + state_preflight.stderr,
        )
        self.assertEqual(
            1,
            lock_preflight.returncode,
            lock_preflight.stdout + lock_preflight.stderr,
        )
        self.assertEqual(
            1,
            root_preflight.returncode,
            root_preflight.stdout + root_preflight.stderr,
        )
        self.assertEqual(1, snapshot.returncode, snapshot.stdout + snapshot.stderr)
        self.assertIn("opaque-owned path 밖", lock_preflight.stderr)
        self.assertIn("opaque-owned path 밖", root_preflight.stderr)
        self.assertIn("opaque-owned path 밖", snapshot.stderr)

    def test_hardlinked_migration_file_is_rejected(self) -> None:
        migrations = self.make_migrations()
        alias = self.project / "application_alias.py"
        try:
            os.link(migrations / "0001_initial.py", alias)
        except OSError as error:
            self.skipTest(f"hardlink unavailable: {error}")

        result = self.run_boundary("snapshot")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("hardlink alias", result.stderr)

    def test_hardlinked_external_owned_file_is_rejected(self) -> None:
        lifecycle_test = self.project / "qa" / "migration_test.py"
        lifecycle_test.parent.mkdir()
        lifecycle_test.write_text("pass\n", encoding="utf-8")
        try:
            os.link(lifecycle_test, self.project / "alias_test.py")
        except OSError as error:
            self.skipTest(f"hardlink unavailable: {error}")

        result = self.run_boundary(
            "snapshot",
            external_owned_opaque_paths=["qa/migration_test.py"],
        )

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("hardlink alias", result.stderr)

    def test_migration_symlink_to_project_root_is_rejected_before_hashing(self) -> None:
        app = self.make_app("orders")
        try:
            (app / "migrations").symlink_to(self.project, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")

        result = self.run_boundary("snapshot")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("저장소 root", result.stderr)

    def test_recovery_accepts_orphans_with_different_exact_opaque_sets(self) -> None:
        qa = self.project / "qa"
        qa.mkdir()
        (qa / "a_test.py").write_text("A = 1\n", encoding="utf-8")
        (qa / "b_test.py").write_text("B = 1\n", encoding="utf-8")
        artifacts = self.project / ".dddjango"
        artifacts.mkdir()
        first = artifacts / "migration-boundary-epoch-first.json"
        second = artifacts / "migration-boundary-epoch-second.json"
        first_result = self.run_boundary(
            "snapshot",
            first,
            ["qa/a_test.py"],
        )
        second_result = self.run_boundary(
            "snapshot",
            second,
            ["qa/a_test.py", "qa/b_test.py"],
        )
        self.assertEqual(0, first_result.returncode, first_result.stderr)
        self.assertEqual(0, second_result.returncode, second_result.stderr)

        recovery = self.run_boundary("recover", artifacts)

        self.assertEqual(0, recovery.returncode, recovery.stdout + recovery.stderr)

    def test_deleted_state_cannot_be_resnapshotted_while_receipt_remains(self) -> None:
        self.snapshot()
        self.state.unlink()

        result = self.run_boundary("snapshot")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("write-once receipt", result.stderr)

    def test_receipt_byte_rewrite_is_rejected(self) -> None:
        self.make_migrations()
        self.snapshot()
        receipt = self.state.with_name(f"{self.state.name}.write-once")
        value = json.loads(receipt.read_text(encoding="utf-8"))
        receipt.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")

        result = self.run_boundary("verify")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("write-once receipt", result.stderr)

    def test_verify_rejects_baseline_replaced_by_same_byte_symlink(self) -> None:
        self.make_migrations()
        self.snapshot()
        copied = self.workspace / "copied-boundary.json"
        copied.write_bytes(self.state.read_bytes())
        self.state.unlink()
        try:
            self.state.symlink_to(copied)
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")

        result = self.run_boundary("verify")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("baseline symlink", result.stderr)

    def test_recovery_rejects_epoch_state_renamed_outside_pattern(self) -> None:
        self.make_migrations()
        artifacts = self.project / ".dddjango" / "20260713-orders"
        artifacts.mkdir(parents=True)
        orphan = artifacts / "migration-boundary-epoch-20260713-120000-01.json"
        snapshot = self.run_boundary("snapshot", orphan)
        self.assertEqual(0, snapshot.returncode, snapshot.stdout + snapshot.stderr)
        orphan.rename(artifacts / "renamed-baseline.json")

        recovery = self.run_boundary("recover", self.project / ".dddjango")

        self.assertEqual(1, recovery.returncode, recovery.stdout + recovery.stderr)
        self.assertIn("receipt의 baseline 파일이 없다", recovery.stderr)

    def test_recovery_rejects_epoch_pair_renamed_with_receipt_suffix(self) -> None:
        self.make_migrations()
        artifacts = self.project / ".dddjango" / "20260713-orders"
        artifacts.mkdir(parents=True)
        orphan = artifacts / "migration-boundary-epoch-20260713-120000-01.json"
        snapshot = self.run_boundary("snapshot", orphan)
        self.assertEqual(0, snapshot.returncode, snapshot.stdout + snapshot.stderr)
        receipt = orphan.with_name(f"{orphan.name}.write-once")
        orphan.rename(artifacts / "renamed-baseline.json")
        receipt.rename(artifacts / "renamed-baseline.json.write-once")

        recovery = self.run_boundary("recover", self.project / ".dddjango")

        self.assertEqual(1, recovery.returncode, recovery.stdout + recovery.stderr)
        self.assertIn("receipt 이름이 변경됐다", recovery.stderr)

    def test_recovery_rejects_epoch_pair_renamed_to_arbitrary_names(self) -> None:
        self.make_migrations()
        artifacts = self.project / ".dddjango" / "20260713-orders"
        artifacts.mkdir(parents=True)
        orphan = artifacts / "migration-boundary-epoch-20260713-120000-01.json"
        snapshot = self.run_boundary("snapshot", orphan)
        self.assertEqual(0, snapshot.returncode, snapshot.stdout + snapshot.stderr)
        receipt = orphan.with_name(f"{orphan.name}.write-once")
        orphan.rename(artifacts / "hidden-baseline.bin")
        receipt.rename(artifacts / "hidden-receipt.bin")

        recovery = self.run_boundary("recover", self.project / ".dddjango")

        self.assertEqual(1, recovery.returncode, recovery.stdout + recovery.stderr)
        self.assertIn("receipt 이름이 변경됐다", recovery.stderr)

    def test_recovery_rejects_epoch_pair_moved_to_another_directory(self) -> None:
        self.make_migrations()
        artifacts_a = self.project / ".dddjango" / "feature-a"
        artifacts_b = self.project / ".dddjango" / "feature-b"
        artifacts_a.mkdir(parents=True)
        artifacts_b.mkdir()
        orphan = artifacts_a / "migration-boundary-epoch-20260713-120000-01.json"
        snapshot = self.run_boundary("snapshot", orphan)
        self.assertEqual(0, snapshot.returncode, snapshot.stdout + snapshot.stderr)
        receipt = orphan.with_name(f"{orphan.name}.write-once")
        orphan.rename(artifacts_b / orphan.name)
        receipt.rename(artifacts_b / receipt.name)

        recovery = self.run_boundary("recover", self.project / ".dddjango")

        self.assertEqual(1, recovery.returncode, recovery.stdout + recovery.stderr)
        self.assertIn("pair 위치가 변경", recovery.stderr)

    def test_snapshot_rejects_state_path_below_symlink_ancestor(self) -> None:
        external = self.workspace / "external_state"
        external.mkdir()
        state_root = self.project / ".dddjango"
        state_root.mkdir()
        linked_feature = state_root / "linked_feature"
        try:
            linked_feature.symlink_to(external, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")
        state = linked_feature / "migration-boundary-epoch-20260713-120000-01.json"

        result = self.run_boundary("snapshot", state)

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("조상에 symlink", result.stderr)

    def test_recovery_ignores_unrelated_symlink_directory(self) -> None:
        artifacts = self.project / ".dddjango"
        artifacts.mkdir()
        external = self.workspace / "external_design"
        external.mkdir()
        link = artifacts / "design-link"
        try:
            link.symlink_to(external, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")

        recovery = self.run_boundary("recover", artifacts)

        self.assertEqual(0, recovery.returncode, recovery.stdout + recovery.stderr)

    def test_missing_baseline_is_infrastructure_error(self) -> None:
        result = self.run_boundary("verify")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("baseline 파일이 없다", result.stderr)

    def test_two_pass_instability_is_an_infrastructure_error(self) -> None:
        spec = importlib.util.spec_from_file_location(
            "dddjango_migration_boundary",
            MIGRATION_CHECK,
        )
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        changed_entry = {
            "path": "orders/migrations/0001_initial.py",
            "kind": "file",
            "sha256": "0" * 64,
        }

        with mock.patch.object(
            module,
            "_scan_migration_tree",
            side_effect=[[], [changed_entry]],
        ):
            with self.assertRaises(module.ManifestError):
                module._stable_scan_migration_tree(self.project)


if __name__ == "__main__":
    unittest.main()
