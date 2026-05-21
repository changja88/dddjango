#!/usr/bin/env python3
"""Validate dddjango skill folders and runtime cache."""

from __future__ import annotations

import re
import sys
import argparse
import os
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT / "workspace"
DEFAULT_PLUGIN_SKILLS = ROOT / "dddjango" / "skills"
DEFAULT_ACTIVE_RUNTIME_SKILLS = (
    Path.home() / ".codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills"
)
DEFAULT_RUNTIME_SKILLS = Path(
    os.environ.get(
        "DDDJANGO_RUNTIME_SKILLS",
        str(DEFAULT_ACTIVE_RUNTIME_SKILLS if DEFAULT_ACTIVE_RUNTIME_SKILLS.exists() else ROOT / "plugins/dddjango/skills"),
    )
)

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
SEQUENTIAL_FALLBACK_NON_EXECUTION_SENTENCE = (
    "When using sequential fallback, explicitly state that real subagents were not executed and that the workflow is being handled as sequential fallback."
)
SEQUENTIAL_FALLBACK_STATUS_SENTENCE = (
    "Real subagents were not executed; this is sequential fallback in the role order below."
)

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
        check.require(
            linked <= reference_files,
            f"{skill_dir.name} links missing reference files: {sorted(linked - reference_files)}",
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
    check.require(
        linked <= reference_files,
        f"{skill_dir.name} links missing reference files: {sorted(linked - reference_files)}",
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
    check.require(
        SEQUENTIAL_FALLBACK_NON_EXECUTION_SENTENCE in skill_text,
        "runtime workflow SKILL.md must explicitly require sequential fallback non-execution reporting",
    )
    check.require(
        SEQUENTIAL_FALLBACK_STATUS_SENTENCE in skill_text,
        "runtime workflow SKILL.md must require the exact sequential fallback status sentence",
    )
    delegation_rules = workflow_skill / "references" / "delegation-rules.md"
    if delegation_rules.is_file():
        delegation_text = read(delegation_rules)
        check.require(
            SEQUENTIAL_FALLBACK_NON_EXECUTION_SENTENCE in delegation_text,
            "runtime delegation-rules.md must explicitly require sequential fallback non-execution reporting",
        )
        check.require(
            SEQUENTIAL_FALLBACK_STATUS_SENTENCE in delegation_text,
            "runtime delegation-rules.md must require the exact sequential fallback status sentence",
        )
    check_reference_links(check, workflow_skill)


def check_source_reference_audit(check: Check, skill_dir: Path) -> None:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return
    text = read(skill_md)
    required = [
        "## Leakage Evidence Protocol",
        "permitted surfaces",
        "concrete artifacts",
        "`not run`",
        "`not provided`",
        "private evaluation material",
        "non-public validation notes",
        "## Public Boundary Wording",
        "public-facing by default",
        "source evidence",
        "review scope",
        "validation conditions",
        "internal eval-pack",
        "traceability manifests",
        "## Runtime-Facing Path Boundary",
        "Runtime-facing guidance",
        "runtime bundle-relative",
        "skill-local",
        "runtime_skill_reference.allow_refs",
        "redacted placeholders",
    ]
    for phrase in required:
        check.require(
            phrase in text,
            f"source-reference-audit must include leakage evidence protocol phrase: {phrase}",
        )
    forbidden = [
        "hidden scoring criteria",
        "hidden expected behavior",
        "hidden target behavior",
        "private scoring text",
        "prior run findings",
        "expected-behavior notes",
        "internal expected behavior",
    ]
    for phrase in forbidden:
        check.require(
            phrase not in text,
            f"source-reference-audit must avoid leakage-prone wording: {phrase}",
        )
    public_boundary = markdown_section(text, "Public Boundary Wording")
    check.require(public_boundary.strip(), "source-reference-audit must include Public Boundary Wording section")
    internal_field_names = [
        "reference_basis",
        "coverage_tags",
        "target_behavior",
        "scoring_checks",
        "hard_gates",
        "evidence_required",
        "failure_modes",
        "expected_outcomes",
        "required_observations",
    ]
    for field_name in internal_field_names:
        check.require(
            f"`{field_name}`" not in public_boundary,
            f"source-reference-audit Public Boundary Wording must keep internal eval-pack field names out: {field_name}",
        )
    check_runtime_facing_path_boundary(check, text)


def check_django_web_skill(check: Check, skill_dir: Path) -> None:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return
    text = read(skill_md)
    required = [
        "display-ready fallback values",
        "`None`, blank strings, and missing optional values",
        "non-empty placeholders",
        "Templates must render prepared display values",
        "empty value path",
        "Changed static files must be referenced by the rendered page",
    ]
    for phrase in required:
        check.require(
            phrase in text,
            f"implementation-django-web must include render fallback/static phrase: {phrase}",
        )


def markdown_section(text: str, heading: str) -> str:
    pattern = re.compile(
        rf"^## {re.escape(heading)}\s*\n(?P<body>.*?)(?=^## |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    return match.group("body") if match else ""


def check_runtime_facing_path_boundary(check: Check, text: str) -> None:
    section = markdown_section(text, "Runtime-Facing Path Boundary")
    check.require(section.strip(), "source-reference-audit must include Runtime-Facing Path Boundary section")
    required = [
        "Authoring/source analysis",
        "cache/source parity evidence",
        "Internal eval/oracle work",
        "Runtime-facing guidance",
        "runtime bundle-relative",
        "skill-local references",
        "Do not present `workspace/reference/**` as runtime-facing allowed refs",
    ]
    for phrase in required:
        check.require(
            phrase in section,
            f"source-reference-audit Runtime-Facing Path Boundary must include phrase: {phrase}",
        )
    for line_number, line in runtime_source_allow_ref_violations(text):
        check.require(
            False,
            f"source-reference-audit must not allow workspace source paths as runtime-facing refs at line {line_number}: {line}",
        )


def runtime_source_allow_ref_violations(text: str) -> list[tuple[int, str]]:
    violations: list[tuple[int, str]] = []
    lines = text.splitlines()
    for index, line in enumerate(lines):
        lowered = line.lower()
        if "workspace/reference" not in lowered:
            continue
        context = "\n".join(lines[max(0, index - 4) : index + 1]).lower()
        if not ("runtime" in context and "allow_refs" in context):
            continue
        if re.search(r"\b(do not|must not|should not|not present|cannot|forbid|forbidden)\b", context):
            continue
        violations.append((index + 1, line.strip()))
    return violations


def check_implementation_tdd_boundaries(check: Check, skill_dir: Path) -> None:
    skill_md = skill_dir / "SKILL.md"
    test_list = skill_dir / "references" / "test-list.md"
    if skill_md.is_file():
        text = read(skill_md)
        check.require(
            "day after expiration rejected" in text
            and "A rejection on another axis" in text,
            "implementation-tdd SKILL.md must require validity-window rejected complements",
        )
    check.require(
        test_list.is_file(),
        "implementation-tdd must include references/test-list.md for boundary guidance",
    )
    if test_list.is_file():
        text = read(test_list)
        check.require(
            "`expires_on` accepted" in text and "`expires_on + 1 day` rejected" in text,
            "implementation-tdd test-list.md must include explicit expiration boundary examples",
        )


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
            if skill_dir.name == "source-reference-audit":
                check_source_reference_audit(check, skill_dir)
            if skill_dir.name == "implementation-tdd":
                check_implementation_tdd_boundaries(check, skill_dir)

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
        if skill_dir.name == "implementation-django-web":
            check_django_web_skill(check, skill_dir)
        if skill_dir.name == "source-reference-audit":
            check_source_reference_audit(check, skill_dir)
        if skill_dir.name == "implementation-tdd":
            check_implementation_tdd_boundaries(check, skill_dir)
        if skill_dir.name == "workflow-dddjango-subagents":
            check_workflow_role_map(check, skill_dir)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--phase",
        choices=["generated", "runtime", "all"],
        default="generated",
        help="generated validates repo skill folders; runtime is cache smoke only; all is the completion gate.",
    )
    parser.add_argument("--skills-dir", type=Path, default=DEFAULT_PLUGIN_SKILLS)
    parser.add_argument("--runtime-skills", type=Path, default=DEFAULT_RUNTIME_SKILLS)
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args(sys.argv[1:])
    check = Check()
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
