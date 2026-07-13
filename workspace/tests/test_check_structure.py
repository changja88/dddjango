from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CHECK_STRUCTURE = REPO_ROOT / "workspace" / "eval" / "tools" / "check-structure.py"


class CheckStructureTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.workspace = Path(self.temporary_directory.name)
        self.project = self.workspace / "project"
        self.project.mkdir()
        self.git("init", "-q")

    def git(self, *args: str) -> None:
        result = subprocess.run(
            ["git", *args],
            cwd=self.project,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def commit(self) -> None:
        self.git("add", ".")
        self.git(
            "-c",
            "user.name=dddjango-test",
            "-c",
            "user.email=dddjango@example.invalid",
            "commit",
            "-q",
            "--allow-empty",
            "-m",
            "baseline",
        )

    def make_actual_app(self, name: str, *, app_config: bool = True) -> Path:
        app = self.project / name
        app.mkdir(parents=True)
        (app / "__init__.py").write_text("", encoding="utf-8")
        if app_config:
            (app / "apps.py").write_text(
                "from django.apps import AppConfig\n"
                "class Config(AppConfig):\n"
                f"    name = {name!r}\n",
                encoding="utf-8",
            )
        (app / "models.py").write_text(
            "from django.db import models\n"
            "class Record(models.Model):\n"
            "    pass\n",
            encoding="utf-8",
        )
        return app

    def run_check(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CHECK_STRUCTURE), str(self.project)],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_ancestor_path_names_do_not_satisfy_structure(self) -> None:
        nested = self.workspace / "application" / "infra_layer" / "django_fake"
        nested.parent.mkdir(parents=True)
        self.project.rename(nested)
        self.project = nested
        self.commit()
        self.make_actual_app("orders")

        result = self.run_check()

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("[SH-1 컨테이너] FAIL-신호", result.stdout)
        self.assertIn("[SH-4 Django앱위치] FAIL-신호", result.stdout)

    def test_existing_utility_package_converted_to_app_is_new_identity(self) -> None:
        package = self.project / "orders"
        package.mkdir()
        (package / "__init__.py").write_text("", encoding="utf-8")
        (package / "helpers.py").write_text("VALUE = 1\n", encoding="utf-8")
        self.commit()
        (package / "apps.py").write_text(
            "from django.apps import AppConfig\n"
            "class OrdersConfig(AppConfig):\n"
            "    name = 'orders'\n",
            encoding="utf-8",
        )

        result = self.run_check()

        self.assertIn("[SH-1 컨테이너] FAIL-신호", result.stdout)
        self.assertIn("orders", result.stdout)

    def test_models_only_django_app_is_discovered(self) -> None:
        self.commit()
        self.make_actual_app("orders", app_config=False)

        result = self.run_check()

        self.assertIn("# 검출 앱(actual AppConfig/Model): ['orders']", result.stdout)
        self.assertIn("[SH-1 컨테이너] FAIL-신호", result.stdout)

    def test_non_django_dataclass_models_module_is_not_an_app(self) -> None:
        self.commit()
        package = self.project / "analytics"
        package.mkdir()
        (package / "__init__.py").write_text("", encoding="utf-8")
        (package / "models.py").write_text(
            "from dataclasses import dataclass\n"
            "@dataclass\n"
            "class Report:\n"
            "    value: int\n",
            encoding="utf-8",
        )

        result = self.run_check()

        self.assertIn("# 검출 앱(actual AppConfig/Model): []", result.stdout)

    def test_established_root_convention_allows_new_root_app(self) -> None:
        self.make_actual_app("legacy")
        self.commit()
        self.make_actual_app("orders")

        result = self.run_check()

        self.assertIn("[SH-1 컨테이너] PASS-신호", result.stdout)
        self.assertIn("[SH-4 Django앱위치] PASS-신호", result.stdout)

    def test_standard_container_wins_in_mixed_layout(self) -> None:
        self.make_actual_app("legacy")
        (self.project / "application").mkdir()
        self.commit()
        self.make_actual_app("orders")

        result = self.run_check()

        self.assertIn("[SH-1 컨테이너] FAIL-신호", result.stdout)
        self.assertIn("[SH-4 Django앱위치] FAIL-신호", result.stdout)

    def test_removed_standard_container_still_wins_from_head(self) -> None:
        self.make_actual_app("legacy")
        application = self.project / "application"
        application.mkdir()
        (application / "__init__.py").write_text("", encoding="utf-8")
        self.commit()
        (application / "__init__.py").unlink()
        application.rmdir()
        self.make_actual_app("orders")

        result = self.run_check()

        self.assertIn("[SH-1 컨테이너] FAIL-신호", result.stdout)
        self.assertIn("[SH-4 Django앱위치] FAIL-신호", result.stdout)

    def test_new_flat_models_package_fails_app_location(self) -> None:
        self.commit()
        models_package = self.project / "orders" / "models"
        models_package.mkdir(parents=True)
        (models_package / "order.py").write_text(
            "from django.db import models\n"
            "class Order(models.Model):\n"
            "    pass\n",
            encoding="utf-8",
        )

        result = self.run_check()

        self.assertIn("# 검출 앱(actual AppConfig/Model): ['orders']", result.stdout)
        self.assertIn("[SH-4 Django앱위치] FAIL-신호", result.stdout)

    def test_new_standard_models_package_passes_app_location(self) -> None:
        self.commit()
        models_package = (
            self.project
            / "application"
            / "orders"
            / "infra_layer"
            / "django_orders"
            / "models"
        )
        models_package.mkdir(parents=True)
        (models_package / "order.py").write_text(
            "from django.db import models\n"
            "class Order(models.Model):\n"
            "    pass\n",
            encoding="utf-8",
        )

        result = self.run_check()

        self.assertIn("[SH-4 Django앱위치] PASS-신호", result.stdout)

    def test_django_named_ancestor_does_not_satisfy_owner_adjacency(self) -> None:
        self.commit()
        app = self.project / "application" / "infra_layer" / "django_container" / "orders"
        app.mkdir(parents=True)
        (app / "models.py").write_text(
            "from django.db import models\n"
            "class Order(models.Model):\n"
            "    pass\n",
            encoding="utf-8",
        )

        result = self.run_check()

        self.assertIn("[SH-4 Django앱위치] FAIL-신호", result.stdout)

    def test_existing_models_package_is_grandfathered(self) -> None:
        models_package = self.project / "orders" / "models"
        models_package.mkdir(parents=True)
        (models_package / "order.py").write_text(
            "from django.db import models\n"
            "class Order(models.Model):\n"
            "    pass\n",
            encoding="utf-8",
        )
        self.commit()

        result = self.run_check()

        self.assertIn("[SH-4 Django앱위치] PASS-신호", result.stdout)
        self.assertIn("grandfather: orders", result.stdout)


if __name__ == "__main__":
    unittest.main()
