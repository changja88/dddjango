from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SYNC_TOOL = REPO_ROOT / "workspace" / "tools" / "corpus_mirror_sync.py"


class CorpusMirrorSyncTest(unittest.TestCase):
    def load_tool(self):
        spec = importlib.util.spec_from_file_location("corpus_mirror_sync", SYNC_TOOL)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_normalization_removes_user_invocable_only_from_frontmatter(self) -> None:
        tool = self.load_tool()
        with tempfile.TemporaryDirectory() as temporary_directory:
            skill = Path(temporary_directory) / "SKILL.md"
            skill.write_text(
                "---\n"
                "name: example\n"
                "user-invocable: false\n"
                "---\n"
                "# Body\n"
                "user-invocable: false\n",
                encoding="utf-8",
            )

            normalized = tool.normalized_skill_text(skill)

            self.assertNotIn("name: example\nuser-invocable: false\n---", normalized)
            self.assertTrue(normalized.endswith("# Body\nuser-invocable: false\n"))

    def test_normalization_fails_closed_without_frontmatter_end(self) -> None:
        tool = self.load_tool()
        with tempfile.TemporaryDirectory() as temporary_directory:
            skill = Path(temporary_directory) / "SKILL.md"
            skill.write_text("---\nname: broken\n", encoding="utf-8")

            with self.assertRaises(tool.StructureError):
                tool.normalized_skill_text(skill)


if __name__ == "__main__":
    unittest.main()
