#!/usr/bin/env python3
"""Tests for validate_plan_governance.py."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import validate_plan_governance as validator


def write(path: Path, text: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_minimal_repo(root: Path) -> None:
    write(
        root / "AGENTS.md",
        "Use workspace/plan/plugin_build_plan.md and workspace/plan/constraint_rules.md.\n",
    )
    for required in validator.REQUIRED_FILES:
        if required == "AGENTS.md":
            continue
        write(root / required, "# file\n")

    write(
        root / "workspace/plan/constraint_rules.md",
        "\n".join(
            [
                "`workspace/plan/**`",
                "`workspace/reference/**`",
                "`workspace/develop/eval/**`",
                "`dddjango/skills/**`",
            ]
        ),
    )
    write(
        root / "workspace/plan/plugin_build_plan.md",
        "workspace/plan/status/phase_status.md\nworkspace/plan/constraint_rules.md\n",
    )
    write(
        root / "workspace/plan/reviews/summaries/20260522-plan-governance-review-summary.md",
        "| finding | closure |\n|---|---|\n| a | b |\nOpen Minor 0\n",
    )

    for directory in validator.REQUIRED_DIRS:
        (root / directory).mkdir(parents=True, exist_ok=True)
        write(root / directory / ".gitkeep")

    for phase, subdirs in validator.PHASES.items():
        phase_dir = root / "workspace/plan/phases" / phase
        write(phase_dir / "index.md", "# index\n")
        for subdir in subdirs:
            write(phase_dir / subdir / ".gitkeep")

    for phase in validator.GOAL_PHASES:
        write(root / "workspace/plan/goals" / phase / ".gitkeep")

    write(
        root / "workspace/plan/decisions/ADR-0001-codex-only-p0-p8-scope.md",
        "Status: accepted\nDate: 2026-05-22\n## Context\n## Decision\n## Consequences\n## Evidence\n",
    )
    write(
        root / "workspace/plan/decisions/ADR-0002-plan-tracking-taxonomy.md",
        "Status: accepted\nDate: 2026-05-22\n## Context\n## Decision\n## Consequences\n## Evidence\n",
    )
    write(
        root / "workspace/plan/decisions/ADR-0003-goal-completion-evidence-policy.md",
        "Status: accepted\nDate: 2026-05-22\n## Context\n## Decision\n## Consequences\n## Evidence\n",
    )


class PlanGovernanceValidatorTests(unittest.TestCase):
    def test_minimal_repo_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_minimal_repo(root)
            self.assertEqual([], validator.validate(root))

    def test_rejects_stale_master_plan_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_minimal_repo(root)
            write(root / "AGENTS.md", "Use workspace/plan/master_plan.md\n")

            failures = validator.validate(root)

            self.assertTrue(any("master_plan.md" in failure for failure in failures))

    def test_rejects_noncanonical_phase_filename(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_minimal_repo(root)
            write(root / "workspace/plan/phases/p2-skill-structure/analysis/bad.md", "수정 대상: x\n")

            failures = validator.validate(root)

            self.assertTrue(any("non-canonical phase filename" in failure for failure in failures))

    def test_rejects_analysis_without_target_line(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_minimal_repo(root)
            write(
                root
                / "workspace/plan/phases/p2-skill-structure/analysis/"
                / "20260522-201530-p2-skill-trigger-boundary-analysis.md",
                "wrong first line\n",
            )

            failures = validator.validate(root)

            self.assertTrue(any("analysis file must start" in failure for failure in failures))

    def test_rejects_pending_index_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_minimal_repo(root)
            write(root / "workspace/plan/indexes/evidence_index.md", "digest: pending\n")

            failures = validator.validate(root)

            self.assertTrue(any("unresolved token" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main()

