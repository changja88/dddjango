from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CLAUDE_SCRIPTS = REPO_ROOT / "dddjango" / "scripts"
CODEX_SCRIPTS = (
    REPO_ROOT / "codex-dddjango" / "skills" / "dddjango" / "scripts"
)


class RuntimeScriptMirrorTest(unittest.TestCase):
    def test_runtime_python_modules_are_byte_identical(self) -> None:
        claude = {path.name: path for path in CLAUDE_SCRIPTS.glob("*.py")}
        codex = {path.name: path for path in CODEX_SCRIPTS.glob("*.py")}

        self.assertEqual(22, len(claude))
        self.assertEqual(set(claude), set(codex))
        self.assertEqual(20, len(tuple(CLAUDE_SCRIPTS.glob("check-*.py"))))
        self.assertNotIn("check-app-container.py", claude)
        self.assertIn("check-migration-boundary.py", claude)
        self.assertIn("check-working-tree-generation.py", claude)
        self.assertIn("promote-run-artifacts.py", claude)
        self.assertIn("migration_scope.py", claude)
        for name in sorted(claude):
            with self.subTest(script=name):
                self.assertEqual(claude[name].read_bytes(), codex[name].read_bytes())


if __name__ == "__main__":
    unittest.main()
