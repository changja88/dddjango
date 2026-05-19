#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import shutil
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

    def test_reference_links_reject_missing_link_targets(self) -> None:
        skill_dir = self.write_skill(
            "linked-skill",
            "test skill with references",
        )
        references = skill_dir / "references"
        references.mkdir()
        (references / "existing.md").write_text("# Existing\n", encoding="utf-8")
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text(
            skill_md.read_text(encoding="utf-8")
            + "\nRead [missing](references/missing.md) when needed.\n",
            encoding="utf-8",
        )
        check = self.validator.Check()

        self.validator.check_reference_links(check, skill_dir)

        self.assertTrue(
            any("links missing reference files" in error for error in check.errors),
            check.errors,
        )

    def test_workflow_reference_links_reject_missing_link_targets(self) -> None:
        repo_root = MODULE_PATH.parents[2]
        source_skill = repo_root / "dddjango" / "skills" / "workflow-dddjango-subagents"
        workflow_skill = self.root / "workflow-dddjango-subagents"
        shutil.copytree(source_skill, workflow_skill)
        skill_md = workflow_skill / "SKILL.md"
        skill_md.write_text(
            skill_md.read_text(encoding="utf-8")
            + "\nRead [missing](references/missing.md) when needed.\n",
            encoding="utf-8",
        )
        check = self.validator.Check()

        self.validator.check_reference_links(check, workflow_skill)

        self.assertTrue(
            any("links missing reference files" in error for error in check.errors),
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

    def test_runtime_source_parity_rejects_reference_drift(self) -> None:
        source_root = self.root / "source-skills"
        runtime_root = self.root / "active-cache-skills"
        source_skill = self.write_skill("source-skills/implementation-django-web", "django web")
        runtime_skill = self.write_skill("active-cache-skills/implementation-django-web", "django web")
        (source_skill / "references").mkdir()
        (runtime_skill / "references").mkdir()
        (source_skill / "references" / "templates.md").write_text("source guidance\n", encoding="utf-8")
        (runtime_skill / "references" / "templates.md").write_text("stale guidance\n", encoding="utf-8")
        check = self.validator.Check()

        self.validator.check_runtime_source_parity(check, source_root, runtime_root)

        self.assertTrue(
            any(
                "implementation-django-web/references/templates.md" in error
                and "differs from source" in error
                for error in check.errors
            ),
            check.errors,
        )

    def test_workflow_role_map_rejects_missing_sequential_fallback_non_execution_instruction(self) -> None:
        repo_root = MODULE_PATH.parents[2]
        source_skill = repo_root / "dddjango" / "skills" / "workflow-dddjango-subagents"
        workflow_skill = self.root / "workflow-dddjango-subagents"
        shutil.copytree(source_skill, workflow_skill)
        skill_md = workflow_skill / "SKILL.md"
        skill_md.write_text(
            skill_md.read_text(encoding="utf-8").replace(
                "When using sequential fallback, explicitly state that real subagents were not executed and that the workflow is being handled as sequential fallback.",
                "",
            ),
            encoding="utf-8",
        )
        check = self.validator.Check()

        self.validator.check_workflow_role_map(check, workflow_skill)

        self.assertTrue(
            any("must explicitly require sequential fallback non-execution reporting" in error for error in check.errors),
            check.errors,
        )

    def test_workflow_role_map_rejects_missing_exact_sequential_fallback_status_sentence(self) -> None:
        repo_root = MODULE_PATH.parents[2]
        source_skill = repo_root / "dddjango" / "skills" / "workflow-dddjango-subagents"
        workflow_skill = self.root / "workflow-dddjango-subagents"
        shutil.copytree(source_skill, workflow_skill)
        sentence = self.validator.SEQUENTIAL_FALLBACK_STATUS_SENTENCE
        for relative in ["SKILL.md", "references/delegation-rules.md"]:
            path = workflow_skill / relative
            path.write_text(path.read_text(encoding="utf-8").replace(sentence, ""), encoding="utf-8")
        check = self.validator.Check()

        self.validator.check_workflow_role_map(check, workflow_skill)

        self.assertTrue(
            any("must require the exact sequential fallback status sentence" in error for error in check.errors),
            check.errors,
        )

    def test_source_reference_audit_rejects_missing_leakage_evidence_protocol(self) -> None:
        repo_root = MODULE_PATH.parents[2]
        source_skill = repo_root / "dddjango" / "skills" / "source-reference-audit"
        skill = self.root / "source-reference-audit"
        shutil.copytree(source_skill, skill)
        skill_md = skill / "SKILL.md"
        skill_md.write_text(
            skill_md.read_text(encoding="utf-8").replace("## Leakage Evidence Protocol", ""),
            encoding="utf-8",
        )
        check = self.validator.Check()

        self.validator.check_source_reference_audit(check, skill)

        self.assertTrue(
            any("source-reference-audit must include leakage evidence protocol phrase" in error for error in check.errors),
            check.errors,
        )

    def test_source_reference_audit_rejects_leakage_prone_wording(self) -> None:
        repo_root = MODULE_PATH.parents[2]
        source_skill = repo_root / "dddjango" / "skills" / "source-reference-audit"
        skill = self.root / "source-reference-audit"
        shutil.copytree(source_skill, skill)
        skill_md = skill / "SKILL.md"
        skill_md.write_text(
            skill_md.read_text(encoding="utf-8") + "\nhidden scoring criteria\nexpected-behavior notes\n",
            encoding="utf-8",
        )
        check = self.validator.Check()

        self.validator.check_source_reference_audit(check, skill)

        self.assertTrue(
            any("must avoid leakage-prone wording" in error for error in check.errors),
            check.errors,
        )

    def test_source_reference_audit_rejects_missing_public_boundary_default(self) -> None:
        repo_root = MODULE_PATH.parents[2]
        source_skill = repo_root / "dddjango" / "skills" / "source-reference-audit"
        skill = self.root / "source-reference-audit"
        shutil.copytree(source_skill, skill)
        skill_md = skill / "SKILL.md"
        skill_md.write_text(
            skill_md.read_text(encoding="utf-8").replace("public-facing by default", "public-oriented usually"),
            encoding="utf-8",
        )
        check = self.validator.Check()

        self.validator.check_source_reference_audit(check, skill)

        self.assertTrue(
            any("public-facing by default" in error for error in check.errors),
            check.errors,
        )

    def test_source_reference_audit_rejects_internal_fields_in_public_boundary_wording(self) -> None:
        repo_root = MODULE_PATH.parents[2]
        source_skill = repo_root / "dddjango" / "skills" / "source-reference-audit"
        skill = self.root / "source-reference-audit"
        shutil.copytree(source_skill, skill)
        skill_md = skill / "SKILL.md"
        skill_md.write_text(
            skill_md.read_text(encoding="utf-8").replace(
                "## Public Boundary Wording\n",
                "## Public Boundary Wording\n\n- Bad public wording: `reference_basis`.\n",
            ),
            encoding="utf-8",
        )
        check = self.validator.Check()

        self.validator.check_source_reference_audit(check, skill)

        self.assertTrue(
            any("Public Boundary Wording must keep internal eval-pack field names out" in error for error in check.errors),
            check.errors,
        )

    def test_source_reference_audit_allows_internal_fields_in_eval_traceability(self) -> None:
        repo_root = MODULE_PATH.parents[2]
        source_skill = repo_root / "dddjango" / "skills" / "source-reference-audit"
        skill = self.root / "source-reference-audit"
        shutil.copytree(source_skill, skill)
        check = self.validator.Check()

        self.validator.check_source_reference_audit(check, skill)

        self.assertFalse(
            any("Public Boundary Wording must keep internal eval-pack field names out" in error for error in check.errors),
            check.errors,
        )

    def test_source_reference_audit_rejects_missing_runtime_facing_path_boundary(self) -> None:
        repo_root = MODULE_PATH.parents[2]
        source_skill = repo_root / "dddjango" / "skills" / "source-reference-audit"
        skill = self.root / "source-reference-audit"
        shutil.copytree(source_skill, skill)
        skill_md = skill / "SKILL.md"
        text = skill_md.read_text(encoding="utf-8")
        before, rest = text.split("## Runtime-Facing Path Boundary\n", 1)
        _, after = rest.split("\n## Conflict And Gap Ledger", 1)
        skill_md.write_text(before + "## Conflict And Gap Ledger" + after, encoding="utf-8")
        check = self.validator.Check()

        self.validator.check_source_reference_audit(check, skill)

        self.assertTrue(
            any("Runtime-Facing Path Boundary" in error for error in check.errors),
            check.errors,
        )

    def test_source_reference_audit_rejects_runtime_allow_refs_to_workspace_source_paths(self) -> None:
        repo_root = MODULE_PATH.parents[2]
        source_skill = repo_root / "dddjango" / "skills" / "source-reference-audit"
        skill = self.root / "source-reference-audit"
        shutil.copytree(source_skill, skill)
        skill_md = skill / "SKILL.md"
        skill_md.write_text(
            skill_md.read_text(encoding="utf-8")
            + "\n```yaml\nruntime_skill_reference:\n  allow_refs:\n    - workspace/docs/**\n```\n",
            encoding="utf-8",
        )
        check = self.validator.Check()

        self.validator.check_source_reference_audit(check, skill)

        self.assertTrue(
            any("must not allow workspace source paths as runtime-facing refs" in error for error in check.errors),
            check.errors,
        )

    def test_source_reference_audit_allows_workspace_paths_as_source_evidence(self) -> None:
        repo_root = MODULE_PATH.parents[2]
        source_skill = repo_root / "dddjango" / "skills" / "source-reference-audit"
        skill = self.root / "source-reference-audit"
        shutil.copytree(source_skill, skill)
        skill_md = skill / "SKILL.md"
        skill_md.write_text(
            skill_md.read_text(encoding="utf-8")
            + "\nSource evidence may compare workspace/docs/** with workspace/reference/** during provenance audits.\n",
            encoding="utf-8",
        )
        check = self.validator.Check()

        self.validator.check_source_reference_audit(check, skill)

        self.assertFalse(
            any("must not allow workspace source paths as runtime-facing refs" in error for error in check.errors),
            check.errors,
        )

    def test_implementation_tdd_rejects_missing_expiration_boundary_guidance(self) -> None:
        repo_root = MODULE_PATH.parents[2]
        source_skill = repo_root / "dddjango" / "skills" / "implementation-tdd"
        skill = self.root / "implementation-tdd"
        shutil.copytree(source_skill, skill)
        skill_md = skill / "SKILL.md"
        skill_md.write_text(
            skill_md.read_text(encoding="utf-8").replace("day after expiration rejected", ""),
            encoding="utf-8",
        )
        test_list = skill / "references" / "test-list.md"
        test_list.write_text(
            test_list.read_text(encoding="utf-8").replace("`expires_on + 1 day` rejected", ""),
            encoding="utf-8",
        )
        check = self.validator.Check()

        self.validator.check_implementation_tdd_boundaries(check, skill)

        self.assertTrue(
            any("implementation-tdd SKILL.md must require validity-window rejected complements" in error for error in check.errors),
            check.errors,
        )
        self.assertTrue(
            any("implementation-tdd test-list.md must include explicit expiration boundary examples" in error for error in check.errors),
            check.errors,
        )

    def test_implementation_tdd_rejects_missing_test_list_reference(self) -> None:
        repo_root = MODULE_PATH.parents[2]
        source_skill = repo_root / "dddjango" / "skills" / "implementation-tdd"
        skill = self.root / "implementation-tdd"
        shutil.copytree(source_skill, skill)
        (skill / "references" / "test-list.md").unlink()
        check = self.validator.Check()

        self.validator.check_implementation_tdd_boundaries(check, skill)

        self.assertTrue(
            any("must include references/test-list.md" in error for error in check.errors),
            check.errors,
        )


if __name__ == "__main__":
    unittest.main()
