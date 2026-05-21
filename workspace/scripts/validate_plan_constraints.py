#!/usr/bin/env python3
"""Validate enforceable workspace plan constraints."""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PLAN_ROOT = REPO_ROOT / "workspace/plan"
SKILL_LV_UP_PLAN_ROOT = PLAN_ROOT / "skill_lv_up_plan"
REFERENCE_LV_UP_PLAN_ROOT = PLAN_ROOT / "reference_lv_up_plan"
EVAL_LV_UP_PLAN_ROOT = PLAN_ROOT / "eval_lv_up_plan"
ETC_LV_UP_PLAN_ROOT = PLAN_ROOT / "etc_lv_up_plan"
SKILLS_ROOT = REPO_ROOT / "dddjango/skills"
REFERENCE_ROOT = REPO_ROOT / "workspace/reference"
BUCKETS = {"response", "code", "plugin", "runtime", "source", "workflow"}
SECTIONS = {"analysis", "plan"}
ANALYSIS_TARGETS = {
    "reference",
    "skill",
    "case",
    "answer",
    "evaluator",
    "runtime-sync",
    "report",
    "model-variance",
    "process",
    "cleanup",
    "tooling",
    "none",
}
TARGETS_BY_PLAN_ROOT = {
    "skill_lv_up_plan": {"skill", "runtime-sync"},
    "reference_lv_up_plan": {"reference"},
    "eval_lv_up_plan": {"case", "answer", "evaluator", "report", "model-variance"},
    "etc_lv_up_plan": {"process", "cleanup", "tooling", "none"},
}
GENERATED_DOC_NAME_PATTERN = re.compile(r"^\d{8}-\d{6}-[a-z0-9][a-z0-9-]*\.md$")
REVIEW_MODE_PATTERN = re.compile(r"^리뷰 방식: (real-subagent|sequential-fallback|not-run)$", re.MULTILINE)
REVIEW_RESULT_PATTERN = re.compile(
    r"^리뷰 결과: Blocker \d+, Major \d+, 열린 Minor \d+$",
    re.MULTILINE,
)


def rel_path(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def first_line(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    return lines[0].strip() if lines else ""


def validate_generated_doc_name(path: Path) -> list[str]:
    findings: list[str] = []
    if not GENERATED_DOC_NAME_PATTERN.fullmatch(path.name):
        findings.append(
            f"{rel_path(path)}: filename must start with YYYYMMDD-HHMMSS- and use kebab-case"
        )
        return findings
    if not path.name.startswith(f"{path.parent.parent.name}-", 16):
        findings.append(
            f"{rel_path(path)}: filename must include target name after timestamp "
            f"('{path.parent.parent.name}')"
        )
    return findings


def validate_analysis_file(path: Path, allowed_targets: set[str] | None = None) -> list[str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    line = lines[0].strip() if lines else ""
    findings: list[str] = []
    prefix = "수정 대상: "
    if not line.startswith(prefix):
        findings.append(f"{rel_path(path)}: first line must start with '수정 대상: '")
        return findings
    target = line.removeprefix(prefix).strip()
    if target not in ANALYSIS_TARGETS:
        allowed = ", ".join(sorted(ANALYSIS_TARGETS))
        findings.append(f"{rel_path(path)}: unknown 수정 대상 '{target}' (allowed: {allowed})")
        return findings
    if allowed_targets is not None and target not in allowed_targets:
        allowed = ", ".join(sorted(allowed_targets))
        findings.append(
            f"{rel_path(path)}: 수정 대상 '{target}' is not allowed here (allowed: {allowed})"
        )
    if not REVIEW_MODE_PATTERN.search(text):
        findings.append(
            f"{rel_path(path)}: analysis must include "
            "'리뷰 방식: real-subagent|sequential-fallback|not-run'"
        )
    if not REVIEW_RESULT_PATTERN.search(text):
        findings.append(
            f"{rel_path(path)}: analysis must include "
            "'리뷰 결과: Blocker N, Major N, 열린 Minor N'"
        )
    return findings


def validate_section_files(
    section_dir: Path,
    section: str,
    allowed_targets: set[str] | None,
) -> list[str]:
    findings: list[str] = []
    for path in sorted(section_dir.iterdir()):
        if path.is_dir():
            findings.append(f"{rel_path(path)}: nested directories are not allowed in {section}/")
            continue
        if path.suffix != ".md":
            findings.append(f"{rel_path(path)}: only .md files are allowed in {section}/")
            continue
        findings.extend(validate_generated_doc_name(path))
        if section == "analysis":
            findings.extend(validate_analysis_file(path, allowed_targets))
    return findings


def validate_plan_pairs(group_dir: Path) -> list[str]:
    analysis_dir = group_dir / "analysis"
    plan_dir = group_dir / "plan"
    if not plan_dir.is_dir():
        return []
    analysis_names = {
        path.name
        for path in analysis_dir.iterdir()
        if path.is_file() and path.suffix == ".md"
    } if analysis_dir.is_dir() else set()
    findings: list[str] = []
    for path in sorted(plan_dir.iterdir()):
        if path.is_file() and path.suffix == ".md" and path.name not in analysis_names:
            findings.append(f"{rel_path(path)}: matching analysis file is required")
    return findings


def has_files(path: Path) -> bool:
    return any(child.is_file() for child in path.rglob("*"))


def reference_areas() -> set[str]:
    if not REFERENCE_ROOT.is_dir():
        return set()
    return {path.name for path in REFERENCE_ROOT.iterdir() if path.is_dir()}


def skill_names() -> set[str]:
    if not SKILLS_ROOT.is_dir():
        return set()
    return {path.name for path in SKILLS_ROOT.iterdir() if path.is_dir()}


def is_topic_name(value: str) -> bool:
    if not value:
        return False
    return all(char.islower() or char.isdigit() or char == "-" for char in value) and (
        value[0].islower() or value[0].isdigit()
    ) and (value[-1].islower() or value[-1].isdigit())


def validate_lv_up_plan(
    root: Path,
    *,
    allowed_groups: set[str] | None,
    group_label: str,
    allowed_targets: set[str],
    topic_names: bool = False,
) -> list[str]:
    if not root.exists():
        return []

    findings: list[str] = []
    for group_dir in sorted(root.iterdir()):
        if not group_dir.is_dir():
            findings.append(f"{rel_path(group_dir)}: only {group_label} directories are allowed here")
            continue
        if allowed_groups is not None and group_dir.name not in allowed_groups:
            allowed = ", ".join(sorted(allowed_groups))
            findings.append(f"{rel_path(group_dir)}: unknown {group_label} (allowed: {allowed})")
            continue
        if topic_names and not is_topic_name(group_dir.name):
            findings.append(
                f"{rel_path(group_dir)}: topic must use lowercase letters, digits, and hyphens"
            )
            continue
        for section_dir in sorted(group_dir.iterdir()):
            if not section_dir.is_dir():
                findings.append(f"{rel_path(section_dir)}: only section directories are allowed here")
                continue
            if section_dir.name not in SECTIONS:
                allowed = ", ".join(sorted(SECTIONS))
                findings.append(f"{rel_path(section_dir)}: unknown section (allowed: {allowed})")
                continue
            if not has_files(section_dir):
                continue
            findings.extend(validate_section_files(section_dir, section_dir.name, allowed_targets))
        findings.extend(validate_plan_pairs(group_dir))
    return findings


def validate_skill_lv_up_plan(root: Path = SKILL_LV_UP_PLAN_ROOT) -> list[str]:
    return validate_lv_up_plan(
        root,
        allowed_groups=skill_names(),
        group_label="skill",
        allowed_targets=TARGETS_BY_PLAN_ROOT["skill_lv_up_plan"],
    )


def validate_reference_lv_up_plan(root: Path = REFERENCE_LV_UP_PLAN_ROOT) -> list[str]:
    return validate_lv_up_plan(
        root,
        allowed_groups=reference_areas(),
        group_label="reference area",
        allowed_targets=TARGETS_BY_PLAN_ROOT["reference_lv_up_plan"],
    )


def validate_eval_lv_up_plan(root: Path = EVAL_LV_UP_PLAN_ROOT) -> list[str]:
    return validate_lv_up_plan(
        root,
        allowed_groups=BUCKETS,
        group_label="bucket",
        allowed_targets=TARGETS_BY_PLAN_ROOT["eval_lv_up_plan"],
    )


def validate_etc_lv_up_plan(root: Path = ETC_LV_UP_PLAN_ROOT) -> list[str]:
    return validate_lv_up_plan(
        root,
        allowed_groups=None,
        group_label="topic",
        allowed_targets=TARGETS_BY_PLAN_ROOT["etc_lv_up_plan"],
        topic_names=True,
    )


def validate_all_plan_constraints() -> list[str]:
    findings: list[str] = []
    findings.extend(validate_skill_lv_up_plan())
    findings.extend(validate_reference_lv_up_plan())
    findings.extend(validate_eval_lv_up_plan())
    findings.extend(validate_etc_lv_up_plan())
    return findings


def main() -> int:
    findings = validate_all_plan_constraints()
    if findings:
        for finding in findings:
            print(f"FAIL: {finding}")
        return 1
    print("OK: plan constraints passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
