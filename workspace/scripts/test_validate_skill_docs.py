#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("validate_skill_docs.py")


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_skill_docs", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ValidateSkillDocsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = load_validator()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def write_skill(self, name: str, description: str) -> Path:
        skill_dir = self.root / name
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            f"""---
name: {name}
description: >
  {description}
---

# Test Skill
""",
            encoding="utf-8",
        )
        return skill_dir

    def write_openai_yaml(self, skill_dir: Path, default_prompt: str = "Use this skill.") -> None:
        agents_dir = skill_dir / "agents"
        agents_dir.mkdir()
        (agents_dir / "openai.yaml").write_text(
            f"""interface:
  display_name: "Test"
  short_description: "Test skill"
  default_prompt: "{default_prompt}"
""",
            encoding="utf-8",
        )

    def test_skill_description_rejects_folded_text_over_runtime_limit(self) -> None:
        skill_dir = self.write_skill("overlong", "x" * 1025)
        check = self.validator.Check()

        self.validator.check_skill_folder(check, skill_dir, require_metadata=False)

        self.assertTrue(
            any("description exceeds 1024 characters" in error for error in check.errors),
            check.errors,
        )

    def test_runtime_cache_checks_non_provisional_skill_descriptions(self) -> None:
        runtime_skills = self.root / "runtime-skills"
        runtime_skills.mkdir()
        self.write_skill("runtime-skills/architecture-db", "x" * 1025)
        check = self.validator.Check()

        self.validator.check_runtime_cache(check, runtime_skills, required=True)

        self.assertTrue(
            any("architecture-db/SKILL.md" in error and "description exceeds" in error for error in check.errors),
            check.errors,
        )

    def test_runtime_source_parity_rejects_openai_yaml_drift(self) -> None:
        source_root = self.root / "source-skills"
        runtime_root = self.root / "runtime-skills"
        source_skill = self.write_skill("source-skills/architecture-db", "database architecture")
        runtime_skill = self.write_skill("runtime-skills/architecture-db", "database architecture")
        self.write_openai_yaml(source_skill, default_prompt="Use $architecture-db from source.")
        self.write_openai_yaml(runtime_skill, default_prompt="Use stale cached prompt.")
        check = self.validator.Check()

        self.validator.check_runtime_source_parity(check, source_root, runtime_root)

        self.assertTrue(
            any("architecture-db/agents/openai.yaml" in error and "differs from source" in error for error in check.errors),
            check.errors,
        )


if __name__ == "__main__":
    unittest.main()
