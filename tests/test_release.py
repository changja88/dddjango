import json
import subprocess
import sys
import tempfile
from pathlib import Path
from contextlib import redirect_stdout
from io import StringIO

import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import release  # noqa: E402


class VersionTests(unittest.TestCase):
    def test_next_version_calculates_semver_bumps(self):
        self.assertEqual(release.next_version("v1.2.2", "patch"), "v1.2.3")
        self.assertEqual(release.next_version("v1.2.2", "minor"), "v1.3.0")
        self.assertEqual(release.next_version("v1.2.2", "major"), "v2.0.0")

    def test_next_version_rejects_invalid_input(self):
        with self.assertRaises(ValueError):
            release.next_version("1.2.2", "patch")

        with self.assertRaises(ValueError):
            release.next_version("v1.2.2", "hotfix")


class FileUpdateTests(unittest.TestCase):
    def test_update_release_files_syncs_plugin_versions_and_readme_tag(self):
        root = self.create_fixture_repo("0.1.0")

        changed = release.update_release_files(root, "v0.2.0")

        self.assertEqual(
            sorted(path.name for path in changed),
            ["README.md", "marketplace.json", "plugin.json", "plugin.json"],
        )

        self.assert_json_version(root / ".codex-plugin/plugin.json", "0.2.0")
        self.assert_json_version(root / ".claude-plugin/plugin.json", "0.2.0")

        marketplace = json.loads((root / ".claude-plugin/marketplace.json").read_text())
        self.assertEqual(marketplace["metadata"]["version"], "0.2.0")
        self.assertEqual(marketplace["plugins"][0]["version"], "0.2.0")

        readme = (root / "README.md").read_text()
        self.assertIn("codex plugin marketplace add changja88/dddjango --ref v0.2.0", readme)
        self.assertIn("Tag the release, for example `v0.2.0`.", readme)

    def test_release_script_dry_run_prints_choices_without_changing_files(self):
        root = self.create_fixture_repo("1.2.2")

        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/release.py"),
                "--dry-run",
                "--root",
                str(root),
            ],
            input="2\n",
            text=True,
            capture_output=True,
            check=True,
        )

        self.assertIn("현재 버전: v1.2.2", result.stdout)
        self.assertIn("1) patch  (v1.2.3)", result.stdout)
        self.assertIn("2) minor  (v1.3.0)", result.stdout)
        self.assertIn("3) major  (v2.0.0)", result.stdout)
        self.assertIn("dry-run: v1.3.0 릴리즈를 준비합니다.", result.stdout)
        self.assert_json_version(root / ".codex-plugin/plugin.json", "1.2.2")

    def test_release_script_reports_dirty_worktree_without_traceback(self):
        root = self.create_fixture_repo("1.2.2")
        subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
        (root / "dirty.txt").write_text("not committed\n")

        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/release.py"),
                "--root",
                str(root),
            ],
            input="1\n",
            text=True,
            capture_output=True,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("릴리즈를 시작할 수 없습니다.", result.stdout)
        self.assertIn("커밋되지 않은 변경사항이 있습니다:", result.stdout)
        self.assertIn("- ?? dirty.txt", result.stdout)

    def create_fixture_repo(self, version):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)
        (root / ".codex-plugin").mkdir()
        (root / ".claude-plugin").mkdir()

        plugin = {
            "name": "dddjango",
            "version": version,
            "homepage": "https://github.com/changja88/dddjango",
            "repository": "https://github.com/changja88/dddjango",
        }
        (root / ".codex-plugin/plugin.json").write_text(
            json.dumps(plugin, indent=2) + "\n"
        )
        (root / ".claude-plugin/plugin.json").write_text(
            json.dumps(plugin, indent=2) + "\n"
        )
        (root / ".claude-plugin/marketplace.json").write_text(
            json.dumps(
                {
                    "metadata": {"version": version},
                    "plugins": [{"name": "dddjango", "version": version}],
                },
                indent=2,
            )
            + "\n"
        )
        (root / "README.md").write_text(
            "\n".join(
                [
                    "codex plugin marketplace add changja88/dddjango --ref v0.1.0",
                    "Tag the release, for example `v0.1.0`.",
                    "",
                ]
            )
        )
        return root

    def assert_json_version(self, path, expected):
        data = json.loads(path.read_text())
        self.assertEqual(data["version"], expected)


class CommandRunTests(unittest.TestCase):
    def test_quiet_run_hides_success_output(self):
        stdout = StringIO()

        with redirect_stdout(stdout):
            release.run(
                [sys.executable, "-c", "print(chr(88) + chr(89) + chr(90))"],
                ROOT,
                quiet=True,
            )

        output = stdout.getvalue()
        self.assertEqual(output, "")
        self.assertNotIn("XYZ", output)


if __name__ == "__main__":
    unittest.main()
