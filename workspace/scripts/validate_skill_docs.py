#!/usr/bin/env python3
"""Validate dddjango planning docs, generated skill folders, and runtime cache."""

from __future__ import annotations

import re
import sys
import argparse
import os
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT / "workspace"
DOCS = WORKSPACE / "docs"
DEFAULT_PLUGIN_SKILLS = ROOT / "dddjango" / "skills"
DEFAULT_RUNTIME_SKILLS = Path(
    os.environ.get(
        "DDDJANGO_RUNTIME_SKILLS",
        str(ROOT / "plugins/dddjango/skills"),
    )
)

REQUIRED_DOCS = [
    "spec.md",
    "reference-index.md",
    "ddd-implementation-standard.md",
    "skill-hierarchy.md",
    "skill-contracts.md",
    "workflow.md",
    "validation-plan.md",
    "plugin-structure.md",
    "skill-authoring.md",
]

PROVISIONAL_SKILLS = [
    "architecture-implementation-patterns",
    "implementation-django-ninja",
    "implementation-django-web",
]

EXPECTED_SKILLS = [
    "source-reference-audit",
    "architecture-ddd",
    "architecture-implementation-patterns",
    "architecture-db",
    "architecture-api",
    "implementation-django",
    "implementation-django-ninja",
    "implementation-django-web",
    "implementation-python",
    "implementation-cleancode",
    "implementation-tdd",
    "implementation-test",
    "workflow-dddjango-subagents",
]

WORKFLOW_ROLES = {
    "Coordinator": ["workflow-dddjango-subagents"],
    "Domain Agent": ["architecture-ddd"],
    "Architecture Agent": ["architecture-implementation-patterns"],
    "DB Agent": ["architecture-db", "implementation-django"],
    "API Agent": ["architecture-api", "implementation-django-ninja"],
    "Django Agent": ["implementation-django", "implementation-django-web", "implementation-python"],
    "Test Agent": ["implementation-tdd", "implementation-test"],
    "Review Agent": ["implementation-cleancode"],
}

ROLE_TABLE_PATTERNS = {
    "Coordinator": re.compile(r"\|\s*Coordinator\s*\|[^|\n]*\|[^|\n]*`workflow-dddjango-subagents`", re.MULTILINE),
    "Domain Agent": re.compile(r"\|\s*Domain Agent\s*\|[^|\n]*\|[^|\n]*`architecture-ddd`", re.MULTILINE),
    "Architecture Agent": re.compile(
        r"\|\s*Architecture Agent\s*\|[^|\n]*\|[^|\n]*`architecture-implementation-patterns`",
        re.MULTILINE,
    ),
    "DB Agent": re.compile(r"\|\s*DB Agent\s*\|[^|\n]*\|[^|\n]*`architecture-db`[^|\n]*`implementation-django`", re.MULTILINE),
    "API Agent": re.compile(r"\|\s*API Agent\s*\|[^|\n]*\|[^|\n]*`architecture-api`[^|\n]*`implementation-django-ninja`", re.MULTILINE),
    "Django Agent": re.compile(
        r"\|\s*Django Agent\s*\|[^|\n]*template/static/web[^|\n]*\|[^|\n]*`implementation-django`[^|\n]*`implementation-django-web`[^|\n]*`implementation-python`",
        re.MULTILINE,
    ),
    "Test Agent": re.compile(r"\|\s*Test Agent\s*\|[^|\n]*\|[^|\n]*`implementation-tdd`[^|\n]*`implementation-test`", re.MULTILINE),
    "Review Agent": re.compile(r"\|\s*Review Agent\s*\|[^|\n]*\|[^|\n]*`implementation-cleancode`", re.MULTILINE),
}

WORKFLOW_REFERENCES = {
    "delegation-rules.md",
    "role-map.md",
    "handoff-contract.md",
    "integration-checklist.md",
}

BANNED_SKILL_DOCS = {
    "README.md",
    "INSTALLATION_GUIDE.md",
    "QUICK_REFERENCE.md",
    "CHANGELOG.md",
}

MAX_DESCRIPTION_CHARS = 1024


class Check:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)

    def warn(self, condition: bool, message: str) -> None:
        if not condition:
            self.warnings.append(message)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def has_frontmatter(text: str) -> bool:
    return bool(re.match(r"^---\n(?P<body>.*?)\n---\n", text, re.DOTALL))


def frontmatter_value(text: str, key: str) -> Optional[str]:
    match = re.match(r"^---\n(?P<body>.*?)\n---\n", text, re.DOTALL)
    if not match:
        return None
    pattern = re.compile(rf"^{re.escape(key)}:\s*(.+)$", re.MULTILINE)
    key_match = pattern.search(match.group("body"))
    if not key_match:
        return None
    return key_match.group(1).strip().strip("\"'")


def frontmatter_block(text: str) -> str:
    match = re.match(r"^---\n(?P<body>.*?)\n---\n", text, re.DOTALL)
    return match.group("body") if match else ""


def frontmatter_description_text(text: str) -> str:
    lines = frontmatter_block(text).splitlines()
    for index, line in enumerate(lines):
        match = re.match(r"^description:\s*(.*)$", line)
        if not match:
            continue
        value = match.group(1).strip()
        if value not in {">", "|"}:
            return value.strip("\"'")
        parts: list[str] = []
        for continuation in lines[index + 1 :]:
            if continuation and not continuation.startswith(" "):
                break
            stripped = continuation.strip()
            if stripped:
                parts.append(stripped)
        return " ".join(parts)
    return ""


def check_frontmatter_yaml_safety(check: Check, skill_md: Path, text: str) -> None:
    frontmatter = frontmatter_block(text)
    for line in frontmatter.splitlines():
        match = re.match(r"^description:\s+(.+)$", line)
        if not match:
            continue
        value = match.group(1).strip()
        if value in {">", "|"} or value.startswith(("'", '"')):
            return
        check.require(
            ": " not in value,
            f"description with ': ' must use a quoted value or block scalar: {skill_md}",
        )


def check_required_docs(check: Check) -> None:
    for name in REQUIRED_DOCS:
        check.require((DOCS / name).is_file(), f"missing docs file: workspace/docs/{name}")


def check_workspace_docs(check: Check) -> None:
    workflow = read(DOCS / "workflow.md")
    plugin_structure = read(DOCS / "plugin-structure.md")
    validation_plan = read(DOCS / "validation-plan.md")

    check.require(
        "canonical source" in workflow
        and "implementation-django-web" in workflow
        and "web template/static" in workflow,
        "workflow.md must declare the role map canonical and include Django web ownership",
    )
    check.require(
        "cache-only" in plugin_structure
        and "workspace canonical source" in plugin_structure
        and "plugin cache" in plugin_structure,
        "plugin-structure.md must forbid cache-only runtime changes",
    )
    check.require(
        "authoring source" in workflow and "runtime bundled reference" in workflow,
        "workflow.md must distinguish source references from runtime bundled references",
    )
    for skill in PROVISIONAL_SKILLS:
        check.require(
            re.search(rf"`{re.escape(skill)}`\s*\|\s*provisional", plugin_structure),
            f"plugin-structure.md must mark {skill} as provisional in the split plan",
        )
    check.require(
        "python3 workspace/scripts/validate_skill_docs.py" in validation_plan,
        "validation-plan.md must name the canonical validation command",
    )
    check.require(
        "--phase all" in validation_plan and "완료 게이트" in validation_plan,
        "validation-plan.md must define --phase all as the completion gate",
    )
    check.require(
        "provisional skill handling" in validation_plan,
        "validation-plan.md must evaluate provisional skill handling",
    )
    check.require(
        "workspace canonical source" in validation_plan,
        "validation-plan.md must require workspace sync after cache edits",
    )
    check.require(
        "## 7. Integration Checklist" in workflow
        and "Domain and invariants" in workflow
        and "Cache sync report" in workflow,
        "workflow.md must define the Integration Checklist required by validation",
    )


def linked_reference_names(skill_text: str) -> set[str]:
    links = set(re.findall(r"\((?:\./)?references/([^)#]+?\.md)(?:#[^)]+)?\)", skill_text))
    inline_refs = set(re.findall(r"`references/([^`]+?\.md)`", skill_text))
    return links | inline_refs


def source_reference_exists(skill_name: str) -> bool:
    return (WORKSPACE / "reference" / skill_name / "reference" / "final.md").is_file()


def check_provisional_marker(check: Check, skill_dir: Path) -> None:
    if skill_dir.name not in PROVISIONAL_SKILLS or source_reference_exists(skill_dir.name):
        return
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return
    text = read(skill_md).lower()
    metadata = frontmatter_block(read(skill_md)).lower()
    check.require(
        "provisional" in metadata and "fallback" in metadata,
        f"{skill_dir.name} frontmatter description must expose provisional status and fallback source",
    )
    check.require(
        "provisional" in text and "fallback" in text,
        f"{skill_dir.name} must declare provisional status and fallback source until dedicated source reference exists",
    )
    openai_yaml = skill_dir / "agents" / "openai.yaml"
    if openai_yaml.is_file():
        metadata = read(openai_yaml).lower()
        check.require(
            "provisional" in metadata or "fallback" in metadata,
            f"{skill_dir.name} agents/openai.yaml must not look complete while source reference is provisional",
        )


def check_reference_links(check: Check, skill_dir: Path) -> None:
    skill_md = skill_dir / "SKILL.md"
    references = skill_dir / "references"
    if not skill_md.is_file() or not references.exists():
        return

    text = read(skill_md)
    linked = linked_reference_names(text)
    reference_files = {path.name for path in references.glob("*.md")}
    if not reference_files:
        return

    if skill_dir.name == "workflow-dddjango-subagents":
        check.require(
            WORKFLOW_REFERENCES <= linked,
            f"{skill_dir.name} SKILL.md must directly link all workflow reference files",
        )
        check.require(
            reference_files <= linked,
            f"{skill_dir.name} has unlinked workflow reference files: {sorted(reference_files - linked)}",
        )
        return

    check.require(
        bool(linked),
        f"{skill_dir.name} SKILL.md must directly link one-level references/*.md files",
    )
    check.require(
        reference_files <= linked,
        f"{skill_dir.name} has unlinked reference files: {sorted(reference_files - linked)}",
    )


def check_skill_folder(check: Check, skill_dir: Path, require_metadata: bool) -> None:
    skill_md = skill_dir / "SKILL.md"
    check.require(skill_md.is_file(), f"missing SKILL.md: {skill_dir}")
    if skill_md.is_file():
        text = read(skill_md)
        check.require(has_frontmatter(text), f"missing frontmatter: {skill_md}")
        check.require(frontmatter_value(text, "name"), f"missing frontmatter name: {skill_md}")
        check.require(
            frontmatter_value(text, "description"),
            f"missing frontmatter description: {skill_md}",
        )
        description = frontmatter_description_text(text)
        check.require(
            len(description) <= MAX_DESCRIPTION_CHARS,
            f"description exceeds {MAX_DESCRIPTION_CHARS} characters: {skill_md}",
        )
        check_frontmatter_yaml_safety(check, skill_md, text)

    openai_yaml = skill_dir / "agents" / "openai.yaml"
    if require_metadata:
        check.require(openai_yaml.is_file(), f"missing agents/openai.yaml: {skill_dir}")
    if openai_yaml.is_file():
        yaml_text = read(openai_yaml)
        check.require("default_prompt:" in yaml_text, f"missing default_prompt: {openai_yaml}")

    for banned in BANNED_SKILL_DOCS:
        check.require(not (skill_dir / banned).exists(), f"banned skill doc exists: {skill_dir / banned}")

    references = skill_dir / "references"
    if references.exists():
        nested = [path for path in references.rglob("*") if path.is_file() and path.parent != references]
        check.require(not nested, f"nested reference files are not allowed: {skill_dir}")
    check_reference_links(check, skill_dir)
    check_provisional_marker(check, skill_dir)


def check_workflow_role_map(check: Check, workflow_skill: Path) -> None:
    skill_md = workflow_skill / "SKILL.md"
    role_map = workflow_skill / "references" / "role-map.md"
    check.require(skill_md.is_file(), f"missing runtime SKILL.md: {skill_md}")
    check.require(role_map.is_file(), f"missing runtime role-map.md: {role_map}")
    if not skill_md.is_file() or not role_map.is_file():
        return

    skill_text = read(skill_md)
    role_text = read(role_map)

    check.require(
        "implementation-django-web" in skill_text
        and "template/static/web" in skill_text
        and "templates/static files" in skill_text,
        "runtime SKILL.md Django Agent must include implementation-django-web and template/static ownership",
    )
    check.require(
        "implementation-django-web" in role_text
        and "template/static/web" in role_text
        and ("templates/**" in role_text or "templates/static files" in role_text)
        and ("static/**" in role_text or "templates/static files" in role_text),
        "runtime role-map.md Django Agent must include implementation-django-web and template/static ownership defaults",
    )
    check.require(
        "`implementation-django`, `implementation-django-web`, `implementation-python`" in role_text,
        "runtime role-map.md Django Agent skill list must match the mandatory template",
    )
    for role, skills in WORKFLOW_ROLES.items():
        check.require(role in skill_text, f"workflow SKILL.md missing role: {role}")
        check.require(role in role_text, f"workflow role-map.md missing role: {role}")
        check.require(
            ROLE_TABLE_PATTERNS[role].search(role_text) is not None,
            f"workflow role-map.md must associate {role} with its expected skills in the same table row",
        )
        for skill in skills:
            check.require(
                skill in skill_text and skill in role_text,
                f"workflow role map must include {skill} for {role}",
            )
    integration_checklist = workflow_skill / "references" / "integration-checklist.md"
    if integration_checklist.is_file():
        checklist_text = read(integration_checklist)
        check.require(
            "Cache sync report" in checklist_text and "workspace canonical source" in checklist_text,
            "runtime integration-checklist.md must include cache sync reporting",
        )
    check.require(
        "Cache sync report" in skill_text and "workspace canonical source" in skill_text,
        "runtime workflow SKILL.md must surface cache sync reporting in its output rules/checklist",
    )
    check.require(
        "wait_agent" in skill_text
        and "close_agent" in skill_text
        and "result collection" in skill_text,
        "runtime workflow SKILL.md must require wait_agent/close_agent result collection before reporting actual subagent completion",
    )
    check.require(
        "Before writing the final answer" in skill_text
        and "If result collection is unavailable or times out" in skill_text,
        "runtime workflow SKILL.md must make subagent result collection a final-answer gate with an explicit blocked fallback",
    )
    check.require(
        "Do not write `wait_agent`, `close_agent`, or result summaries in the final answer unless those calls actually completed." in skill_text,
        "runtime workflow SKILL.md must prohibit fabricated result-collection claims",
    )
    check_reference_links(check, workflow_skill)


def runtime_facing_files(skill_dir: Path) -> set[Path]:
    files = {Path("SKILL.md"), Path("agents/openai.yaml")}
    references = skill_dir / "references"
    if references.is_dir():
        files.update(Path("references") / path.name for path in references.glob("*.md"))
    return files


def check_runtime_source_parity(check: Check, source_skills: Path, runtime_skills: Path) -> None:
    for skill_name in EXPECTED_SKILLS:
        source_skill = source_skills / skill_name
        runtime_skill = runtime_skills / skill_name
        if not source_skill.is_dir() or not runtime_skill.is_dir():
            continue
        rel_files = runtime_facing_files(source_skill) | runtime_facing_files(runtime_skill)
        for rel_file in sorted(rel_files):
            source_file = source_skill / rel_file
            runtime_file = runtime_skill / rel_file
            display = f"{skill_name}/{rel_file.as_posix()}"
            if not source_file.is_file():
                check.require(False, f"runtime cache has file absent from source: {display}")
                continue
            if not runtime_file.is_file():
                check.require(False, f"runtime cache missing source file: {display}")
                continue
            if source_file.read_bytes() != runtime_file.read_bytes():
                check.require(False, f"runtime cache differs from source: {display}")


def check_runtime_cache(
    check: Check,
    runtime_skills: Path,
    required: bool,
    source_skills: Path | None = None,
) -> None:
    if not runtime_skills.exists():
        message = f"runtime skills folder not found: {runtime_skills}"
        if required:
            check.errors.append(message)
        else:
            check.warnings.append(f"{message}; skipped")
        return
    for skill_name in EXPECTED_SKILLS:
        skill_dir = runtime_skills / skill_name
        check.require(skill_dir.is_dir(), f"missing runtime skill folder: {skill_dir}")
        if skill_dir.is_dir():
            check_skill_folder(check, skill_dir, require_metadata=False)

    workflow_skill = runtime_skills / "workflow-dddjango-subagents"
    check_workflow_role_map(check, workflow_skill)
    if source_skills is not None:
        check_runtime_source_parity(check, source_skills, runtime_skills)


def check_generated_skills(check: Check, skills_dir: Path, required: bool) -> None:
    if not skills_dir.exists():
        message = f"generated skills folder not found: {skills_dir}"
        if required:
            check.errors.append(message)
        else:
            check.warnings.append(f"{message}; skipped")
        return

    for skill_name in EXPECTED_SKILLS:
        check.require((skills_dir / skill_name).is_dir(), f"missing expected generated skill: {skill_name}")

    for skill_dir in sorted(path for path in skills_dir.iterdir() if path.is_dir()):
        check_skill_folder(check, skill_dir, require_metadata=True)
        if skill_dir.name == "workflow-dddjango-subagents":
            check_workflow_role_map(check, skill_dir)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--phase",
        choices=["docs", "generated", "runtime", "all"],
        default="docs",
        help="docs validates planning docs only; generated requires repo skill folders; runtime is cache smoke only; all is the completion gate.",
    )
    parser.add_argument("--skills-dir", type=Path, default=DEFAULT_PLUGIN_SKILLS)
    parser.add_argument("--runtime-skills", type=Path, default=DEFAULT_RUNTIME_SKILLS)
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args(sys.argv[1:])
    check = Check()
    check_required_docs(check)
    if not check.errors:
        check_workspace_docs(check)
        if args.phase in {"generated", "all"}:
            check_generated_skills(check, args.skills_dir, required=True)
        if args.phase in {"runtime", "all"}:
            source_skills = args.skills_dir if args.phase == "all" else None
            check_runtime_cache(
                check,
                args.runtime_skills,
                required=True,
                source_skills=source_skills,
            )
        if args.phase == "runtime":
            check.warnings.append(
                "runtime phase is a smoke check only; it is not a completion gate without --phase generated or --phase all"
            )

    for warning in check.warnings:
        print(f"WARN: {warning}")
    for error in check.errors:
        print(f"ERROR: {error}")

    if check.errors:
        print(f"FAILED: {len(check.errors)} error(s), {len(check.warnings)} warning(s)")
        return 1
    print(f"OK: validation passed with {len(check.warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
