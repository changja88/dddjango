#!/usr/bin/env python3
"""Validate dddjango rebuild planning governance files."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


PHASES: dict[str, tuple[str, ...]] = {
    "p0-inventory": ("analysis", "plan", "evidence", "closure"),
    "p1-reference-sufficiency": ("analysis", "plan", "evidence", "closure"),
    "p1-5-usage-cards": ("cards", "evidence", "closure"),
    "p2-skill-structure": ("analysis", "plan", "evidence", "closure"),
    "p3-forward-tests": ("prompts", "evidence", "closure"),
    "p4-eval-skeleton": ("analysis", "plan", "fixtures", "evidence", "closure"),
    "p4-5-runtime-parity": ("analysis", "plan", "evidence", "closure"),
    "p5-individual-eval": ("analysis", "plan", "evidence", "closure"),
    "p6-integration-eval": ("analysis", "plan", "evidence", "closure"),
    "p7-install-packaging": ("analysis", "plan", "evidence", "closure"),
    "p8-full-regression": ("analysis", "plan", "evidence", "closure"),
}

GOAL_PHASES = (
    "p2-skill-structure",
    "p3-forward-tests",
    "p4-eval-skeleton",
    "p4-5-runtime-parity",
    "p5-individual-eval",
    "p6-integration-eval",
    "p7-install-packaging",
    "p8-full-regression",
)

REQUIRED_FILES = (
    "AGENTS.md",
    "workspace/plan/README.md",
    "workspace/plan/plugin_build_plan.md",
    "workspace/plan/constraint_rules.md",
    "workspace/plan/governance/naming_convention.md",
    "workspace/plan/governance/failure_taxonomy.md",
    "workspace/plan/status/phase_status.md",
    "workspace/plan/status/current_focus.md",
    "workspace/plan/status/open_risks.md",
    "workspace/plan/status/superseded_index.md",
    "workspace/plan/status/rebuild_changelog.md",
    "workspace/plan/indexes/artifact_index.md",
    "workspace/plan/indexes/evidence_index.md",
    "workspace/plan/indexes/review_index.md",
    "workspace/plan/indexes/goal_index.md",
    "workspace/plan/decisions/index.md",
    "workspace/plan/decisions/ADR-0001-codex-only-p0-p8-scope.md",
    "workspace/plan/decisions/ADR-0002-plan-tracking-taxonomy.md",
    "workspace/plan/decisions/ADR-0003-goal-completion-evidence-policy.md",
)

REQUIRED_DIRS = (
    "workspace/plan/archive/superseded",
    "workspace/plan/goals/approvals",
    "workspace/plan/goals/closures",
    "workspace/plan/reviews/raw",
    "workspace/plan/reviews/summaries",
    "workspace/plan/reviews/closures",
)

CANONICAL_RE = re.compile(
    r"^\d{8}-\d{6}-"
    r"(p0|p1|p1-5|p2|p3|p4|p4-5|p5|p6|p7|p8|p9)-"
    r"(plugin|skill|reference|eval|runtime|install|review|governance|goal|workflow)-"
    r"[a-z0-9]+(?:-[a-z0-9]+)*-"
    r"(analysis|plan|evidence|closure|prompt|review|raw|decision|index|fixture|inventory|protocol)\.md$"
)

ADR_RE = re.compile(r"^ADR-\d{4}-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
FORBIDDEN_STATUS_TOKENS = (
    "pending recheck",
    "pending-after",
    "input digest: pending",
    "digest: pending",
)
STALE_PATHS = (
    "workspace/plan/master_plan.md",
    "workspace/plan/eval_protocol.md",
    "workspace/plan/plugin_inventory.md",
    "workspace/plan/usage_cards.md",
    "workspace/plan/forward_tests/",
    "workspace/plan/install_evidence/",
)
FORBIDDEN_SKILL_DOC_NAMES = {
    "README.md",
    "INSTALLATION_GUIDE.md",
    "QUICK_REFERENCE.md",
    "CHANGELOG.md",
}


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def first_nonempty_line(path: Path) -> str:
    for line in read_text(path).splitlines():
        if line.strip():
            return line.strip()
    return ""


def validate(root: Path) -> list[str]:
    root = root.resolve()
    failures: list[str] = []

    for item in REQUIRED_FILES:
        path = root / item
        if not path.is_file():
            failures.append(f"missing required file: {item}")

    for item in REQUIRED_DIRS:
        path = root / item
        if not path.is_dir():
            failures.append(f"missing required directory: {item}")

    plan_root = root / "workspace/plan"
    phase_root = plan_root / "phases"
    for phase, subdirs in PHASES.items():
        phase_dir = phase_root / phase
        if not phase_dir.is_dir():
            failures.append(f"missing phase directory: {rel(phase_dir, root)}")
            continue
        index = phase_dir / "index.md"
        if not index.is_file():
            failures.append(f"missing phase index: {rel(index, root)}")
        for subdir in subdirs:
            child = phase_dir / subdir
            if not child.is_dir():
                failures.append(f"missing phase subdirectory: {rel(child, root)}")
            elif not any(child.iterdir()):
                failures.append(f"empty untracked phase subdirectory: {rel(child, root)}")

    goal_root = plan_root / "goals"
    for phase in GOAL_PHASES:
        phase_dir = goal_root / phase
        if not phase_dir.is_dir():
            failures.append(f"missing goal prompt directory: {rel(phase_dir, root)}")
        elif not any(phase_dir.iterdir()):
            failures.append(f"empty untracked goal prompt directory: {rel(phase_dir, root)}")

    if (root / "AGENTS.md").is_file():
        agents = read_text(root / "AGENTS.md")
        if "workspace/plan/plugin_build_plan.md" not in agents:
            failures.append("AGENTS.md does not reference workspace/plan/plugin_build_plan.md")
        if "workspace/plan/constraint_rules.md" not in agents:
            failures.append("AGENTS.md does not reference workspace/plan/constraint_rules.md")
        if "workspace/plan/master_plan.md" in agents:
            failures.append("AGENTS.md still references workspace/plan/master_plan.md")

    if (plan_root / "constraint_rules.md").is_file():
        constraints = read_text(plan_root / "constraint_rules.md")
        for scope in (
            "workspace/plan/**",
            "workspace/reference/**",
            "workspace/develop/eval/**",
            "dddjango/skills/**",
        ):
            if scope not in constraints:
                failures.append(f"constraint_rules.md does not include scope {scope}")

    if (plan_root / "plugin_build_plan.md").is_file():
        master_plan = read_text(plan_root / "plugin_build_plan.md")
        if "workspace/plan/status/phase_status.md" not in master_plan:
            failures.append("plugin_build_plan.md does not identify phase_status.md as source of truth")
        if "workspace/plan/constraint_rules.md" not in master_plan:
            failures.append("plugin_build_plan.md does not reference constraint_rules.md")

    stale_check_files = [
        root / "AGENTS.md",
        plan_root / "plugin_build_plan.md",
        plan_root / "status/phase_status.md",
    ]
    for path in stale_check_files:
        if not path.is_file():
            continue
        text = read_text(path)
        for stale_path in STALE_PATHS:
            if stale_path in text:
                failures.append(f"{rel(path, root)} contains stale path {stale_path}")

    for index in (plan_root / "indexes").glob("*.md"):
        text = read_text(index)
        lowered = text.lower()
        for token in FORBIDDEN_STATUS_TOKENS:
            if token in lowered:
                failures.append(f"{rel(index, root)} contains unresolved token {token!r}")

    for phase_dir in phase_root.glob("p*"):
        if not phase_dir.is_dir():
            continue
        for kind in ("analysis", "plan", "evidence", "closure", "cards", "prompts", "fixtures"):
            child = phase_dir / kind
            if not child.is_dir():
                continue
            for path in child.glob("*.md"):
                if not CANONICAL_RE.match(path.name):
                    failures.append(f"non-canonical phase filename: {rel(path, root)}")

    for phase_dir in goal_root.glob("p*"):
        if not phase_dir.is_dir():
            continue
        for path in phase_dir.glob("*.md"):
            if path.name == "README.md":
                continue
            if not CANONICAL_RE.match(path.name):
                failures.append(f"non-canonical goal filename: {rel(path, root)}")

    for path in phase_root.glob("*/analysis/*.md"):
        if not first_nonempty_line(path).startswith("수정 대상: "):
            failures.append(f"analysis file must start with '수정 대상: ': {rel(path, root)}")
    for path in phase_root.glob("*/plan/*.md"):
        if not first_nonempty_line(path).startswith("수정 대상: "):
            failures.append(f"plan file must start with '수정 대상: ': {rel(path, root)}")

    for path in (plan_root / "decisions").glob("*.md"):
        if path.name == "index.md":
            continue
        if not ADR_RE.match(path.name):
            failures.append(f"non-canonical ADR filename: {rel(path, root)}")
        text = read_text(path)
        for heading in ("Status:", "Date:", "## Context", "## Decision", "## Consequences", "## Evidence"):
            if heading not in text:
                failures.append(f"{rel(path, root)} missing ADR field {heading}")

    summary = plan_root / "reviews/summaries/20260522-plan-governance-review-summary.md"
    if summary.is_file():
        text = read_text(summary)
        if "| finding | closure |" not in text:
            failures.append("plan governance review summary lacks finding closure table")
        if "Open Minor 0" not in text:
            failures.append("plan governance review summary does not record Open Minor 0")

    for path in (root / "dddjango/skills").glob("**/*"):
        if path.is_file() and path.name in FORBIDDEN_SKILL_DOC_NAMES:
            failures.append(f"forbidden process/support doc inside skill folder: {rel(path, root)}")

    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="repository root to validate")
    args = parser.parse_args(argv)

    failures = validate(Path(args.root))
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("OK: plan governance validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

