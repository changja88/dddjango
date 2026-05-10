#!/usr/bin/env python3
"""Validate dddjango plugin eval protocol isolation artifacts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path("/Users/hyun/Desktop/dddjango")
PUBLIC_CASES = REPO_ROOT / "workspace/develop/eval/response/cases/plugin/public"
VARIANTS = ("baseline", "with-dddjango")

PUBLIC_PACKET_FORBIDDEN_PATTERNS = {
    "artifact persistence": re.compile(r"\b(output to save|artifact|raw output|prompt-input/debug)\b", re.I),
    "operator transcript": re.compile(r"\bcommand transcript|commands actually run|not-run checks\b", re.I),
    "absolute repo path": re.compile(re.escape(str(REPO_ROOT))),
    "private evaluator wording": re.compile(r"\bprivate evaluator|prior run findings\b", re.I),
    "private route key wording": re.compile(r"\bexpected route|intended route|scoring note|hidden failure\b", re.I),
}

BASELINE_CONTAMINATION_PATTERNS = {
    "dddjango skill metadata": re.compile(r"dddjango:[a-z0-9_-]+", re.I),
    "runtime cache path": re.compile(r"dddjango-local/dddjango|plugins/cache/dddjango", re.I),
    "canonical plugin source path": re.compile(re.escape(str(REPO_ROOT / "dddjango"))),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--case", action="append", dest="cases")
    parser.add_argument("--variant", action="append", choices=VARIANTS)
    parser.add_argument("--public-cases-dir", type=Path, default=PUBLIC_CASES)
    parser.add_argument("--skip-run-artifacts", action="store_true")
    return parser.parse_args()


def selected_case_ids(public_cases_dir: Path, selected: list[str] | None) -> list[str]:
    case_ids = sorted(path.stem for path in public_cases_dir.glob("case-*.md") if path.stem != "case-101")
    if not selected:
        return case_ids
    known = set(case_ids)
    missing = sorted(set(selected) - known)
    if missing:
        raise AssertionError(f"unknown public case(s): {', '.join(missing)}")
    return [case_id for case_id in case_ids if case_id in set(selected)]


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise AssertionError(f"missing JSON artifact: {path}") from exc
    except json.JSONDecodeError as exc:
        raise AssertionError(f"invalid JSON artifact: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise AssertionError(f"JSON artifact must be an object: {path}")
    return value


def lint_public_packets(public_cases_dir: Path) -> list[str]:
    findings: list[str] = []
    for path in sorted(public_cases_dir.glob("case-*.md")):
        text = path.read_text(encoding="utf-8")
        for label, pattern in PUBLIC_PACKET_FORBIDDEN_PATTERNS.items():
            if pattern.search(text):
                findings.append(f"{path.relative_to(REPO_ROOT)}: {label}")
    return findings


def validate_run_completeness(run_dir: Path, case_ids: list[str], variants: list[str]) -> list[str]:
    findings: list[str] = []
    required_names = [
        "{case_id}-{variant}.txt",
        "{case_id}-{variant}-events.jsonl",
        "{case_id}-{variant}.stderr.txt",
        "{case_id}-{variant}-command.txt",
        "{case_id}-{variant}-exit.txt",
    ]
    for case_id in case_ids:
        prompt_path = run_dir / "raw" / f"{case_id}-public-prompt.md"
        operator_prompt_path = run_dir / "raw" / f"{case_id}-operator-prompt.txt"
        if not prompt_path.is_file():
            findings.append(f"missing public prompt artifact: {prompt_path}")
        if not operator_prompt_path.is_file():
            findings.append(f"missing operator prompt artifact: {operator_prompt_path}")
        stale_prompt_inputs = [
            run_dir / "raw" / f"{case_id}-prompt-input.json",
            run_dir / "raw" / f"{case_id}-prompt-input.stderr.txt",
        ]
        for path in stale_prompt_inputs:
            if path.exists():
                findings.append(f"stale unscoped prompt-input artifact must be removed: {path}")
        baseline_prompt_inputs = [
            run_dir / "raw" / f"{case_id}-baseline-prompt-input.json",
            run_dir / "raw" / f"{case_id}-baseline-prompt-input.stderr.txt",
        ]
        for path in baseline_prompt_inputs:
            if path.exists():
                findings.append(f"baseline prompt-input artifact is forbidden: {path}")
        if "with-dddjango" in variants:
            with_prompt_inputs = [
                run_dir / "raw" / f"{case_id}-with-dddjango-prompt-input.json",
                run_dir / "raw" / f"{case_id}-with-dddjango-prompt-input.stderr.txt",
            ]
            for path in with_prompt_inputs:
                if not path.is_file():
                    findings.append(f"missing with-dddjango prompt-input artifact: {path}")
        for variant in variants:
            for name_template in required_names:
                path = run_dir / "raw" / name_template.format(case_id=case_id, variant=variant)
                if not path.is_file():
                    findings.append(f"missing {variant} artifact: {path}")
            exit_path = run_dir / "raw" / f"{case_id}-{variant}-exit.txt"
            if exit_path.is_file() and exit_path.read_text(encoding="utf-8").strip() != "0":
                findings.append(f"{case_id} {variant} exit is not 0: {exit_path.read_text(encoding='utf-8').strip()}")
    return findings


def validate_baseline_isolation(run_dir: Path, case_ids: list[str]) -> list[str]:
    findings: list[str] = []
    for case_id in case_ids:
        path = run_dir / "raw" / f"{case_id}-baseline-isolation.json"
        artifact = load_json(path)
        if artifact.get("pass") is not True:
            findings.append(f"{case_id}: baseline isolation artifact pass=false")
        if artifact.get("forbiddenPathsAbsent") is not True:
            findings.append(f"{case_id}: forbidden baseline paths are present")
        if artifact.get("commandUsesIgnoreUserConfig") is not True:
            findings.append(f"{case_id}: baseline command missing --ignore-user-config")
        if artifact.get("commandUsesIgnoreRules") is not True:
            findings.append(f"{case_id}: baseline command missing --ignore-rules")
        if artifact.get("runsFromOriginalRepoRoot") is True:
            findings.append(f"{case_id}: baseline runs from original repo root")
        if artifact.get("operatorPromptContainsOriginalRepoRoot") is True:
            findings.append(f"{case_id}: baseline operator prompt contains original repo root")
        metadata_mentions = artifact.get("operatorPromptDddjangoSkillMetadataMentions")
        if metadata_mentions:
            findings.append(f"{case_id}: baseline operator prompt contains dddjango skill metadata names")
    return findings


def contamination_scan(run_dir: Path, case_ids: list[str]) -> list[str]:
    findings: list[str] = []
    suffixes = ["baseline.txt"]
    for case_id in case_ids:
        for suffix in suffixes:
            path = run_dir / "raw" / f"{case_id}-{suffix}"
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for label, pattern in BASELINE_CONTAMINATION_PATTERNS.items():
                if pattern.search(text):
                    findings.append(f"{path.relative_to(run_dir)}: {label}")
    return findings


def main() -> int:
    args = parse_args()
    run_dir = args.run_dir if args.run_dir.is_absolute() else REPO_ROOT / args.run_dir
    public_cases_dir = (
        args.public_cases_dir
        if args.public_cases_dir.is_absolute()
        else REPO_ROOT / args.public_cases_dir
    )
    case_ids = selected_case_ids(public_cases_dir, args.cases)
    variants = args.variant or list(VARIANTS)

    findings = lint_public_packets(public_cases_dir)
    if not args.skip_run_artifacts:
        findings.extend(validate_run_completeness(run_dir, case_ids, variants))
        if "baseline" in variants:
            findings.extend(validate_baseline_isolation(run_dir, case_ids))
            findings.extend(contamination_scan(run_dir, case_ids))

    if findings:
        for finding in findings:
            print(f"FAIL: {finding}")
        raise SystemExit(1)

    print(
        "eval protocol validation passed: "
        f"{len(case_ids)} public case(s), variants={','.join(variants)}, "
        f"run_artifacts={'skipped' if args.skip_run_artifacts else 'checked'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
