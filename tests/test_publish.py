import subprocess
import sys
import tempfile
from pathlib import Path
from contextlib import redirect_stdout
from io import StringIO
from unittest import mock

import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import publish  # noqa: E402


class PublishTests(unittest.TestCase):
    def test_latest_semver_tag_uses_highest_version(self):
        root = self.create_git_repo()
        self.git(root, "tag", "v0.9.9")
        self.git(root, "tag", "v1.0.0")
        self.git(root, "tag", "not-a-release")

        self.assertEqual(publish.latest_semver_tag(root), "v1.0.0")

    def test_publish_pushes_current_branch_and_latest_tag(self):
        root = Path("/repo")
        calls = []

        def fake_run(command, _root, *, quiet=False):
            calls.append(command)
            if command == ["git", "rev-parse", "--is-inside-work-tree"]:
                return subprocess.CompletedProcess(command, 0, stdout="true\n")
            if command == ["git", "branch", "--show-current"]:
                return subprocess.CompletedProcess(command, 0, stdout="main\n")
            if command == ["git", "tag", "--list"]:
                return subprocess.CompletedProcess(command, 0, stdout="v0.1.1\nv0.1.2\n")
            return subprocess.CompletedProcess(command, 0, stdout="")

        with mock.patch("publish.run", side_effect=fake_run), redirect_stdout(StringIO()):
            publish.publish(root)

        self.assertIn(["git", "push", "origin", "main"], calls)
        self.assertIn(["git", "push", "origin", "v0.1.2"], calls)

    def create_git_repo(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)
        self.git(root, "init")
        self.git(root, "config", "user.email", "test@example.com")
        self.git(root, "config", "user.name", "Test User")
        (root / "README.md").write_text("test\n")
        self.git(root, "add", "README.md")
        self.git(root, "commit", "-m", "initial")
        return root

    def git(self, root, *args):
        return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)


if __name__ == "__main__":
    unittest.main()
