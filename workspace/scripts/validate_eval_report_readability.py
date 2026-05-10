#!/usr/bin/env python3
"""Validate that generated eval reports expose readable artifact views."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


REPO_ROOT = Path("/Users/hyun/Desktop/dddjango")
DEFAULT_REPORT = REPO_ROOT / "workspace/develop/evals/runs/20260510-0900-plugin-eval/report.html"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument(
        "--require-code-artifacts",
        action="store_true",
        help="Require embedded code-backed changed-files and diff artifacts.",
    )
    return parser.parse_args()


def extract_report_data(report_html: str) -> dict[str, object]:
    match = re.search(r"const REPORT_DATA = (.*?);\n", report_html, re.S)
    if not match:
        raise AssertionError("REPORT_DATA block was not found")
    return json.loads(match.group(1))


def main() -> int:
    args = parse_args()
    html = args.report.read_text(encoding="utf-8")
    data = extract_report_data(html)
    embedded = data.get("embeddedArtifacts")
    if not isinstance(embedded, dict) or not embedded:
        raise AssertionError("embeddedArtifacts must be a non-empty object")

    kinds = {artifact.get("kind") for artifact in embedded.values() if isinstance(artifact, dict)}
    required_kinds = {
        "case-analysis",
        "case-output",
        "command",
        "empty",
        "json",
        "jsonl",
        "markdown",
    }
    missing_kinds = sorted(required_kinds - kinds)
    if missing_kinds:
        raise AssertionError(f"missing readable artifact kinds: {', '.join(missing_kinds)}")

    case_rows = data.get("caseComparisons")
    case_ids = [
        str(row.get("case"))
        for row in case_rows
        if isinstance(row, dict) and row.get("case")
    ] if isinstance(case_rows, list) else []

    if "case-003" in case_ids:
        required_artifacts = {
            "analysis/case-003.html": "case-analysis",
            "raw/case-003-with-dddjango.txt": "case-output",
            "raw/case-003-public-prompt.md": "markdown",
            "raw/case-003-prompt-input.json": "json",
            "raw/case-003-with-dddjango-events.jsonl": "jsonl",
            "raw/case-003-with-dddjango-command.txt": "command",
            "raw/cache-source-diff.txt": "empty",
        }
    else:
        if not case_ids:
            raise AssertionError("caseComparisons must contain at least one case")
        first_case = case_ids[0]
        required_artifacts = {
            f"analysis/{first_case}.html": "case-analysis",
            f"raw/{first_case}-with-dddjango.txt": "case-output",
            f"raw/{first_case}-public-prompt.md": "markdown",
            f"raw/{first_case}-prompt-input.json": "json",
            f"raw/{first_case}-with-dddjango-events.jsonl": "jsonl",
            f"raw/{first_case}-with-dddjango-command.txt": "command",
        }
        if args.require_code_artifacts:
            required_artifacts.update(
                {
                    f"code/{first_case}/baseline/changed-files.json": "changed-files",
                    f"code/{first_case}/baseline/diff.patch": "diff",
                    f"code/{first_case}/with-dddjango/changed-files.json": "changed-files",
                    f"code/{first_case}/with-dddjango/diff.patch": "diff",
                }
            )
    for href, expected_kind in required_artifacts.items():
        artifact = embedded.get(href)
        if not isinstance(artifact, dict):
            raise AssertionError(f"missing embedded artifact: {href}")
        actual_kind = artifact.get("kind")
        if actual_kind != expected_kind:
            raise AssertionError(f"{href} kind mismatch: expected {expected_kind}, got {actual_kind}")

    required_tokens = [
        "artifact-tabs",
        "renderMarkdownArtifact",
        "renderJsonArtifact",
        "renderJsonlArtifact",
        "renderCaseOutputArtifact",
        "renderCommandArtifact",
        "renderArtifactMetadata",
        "renderSourceFileArtifact",
        "renderDiffArtifact",
        "renderChangedFilesArtifact",
        "renderCodeBlock",
        "renderCaseCodeComparison",
        "response-only",
        "No code captured",
    ]
    missing_tokens = [token for token in required_tokens if token not in html]
    if missing_tokens:
        raise AssertionError(f"missing readable viewer tokens: {', '.join(missing_tokens)}")

    if args.require_code_artifacts:
        code_kinds = {"changed-files", "diff", "source-file"}
        missing_code_kinds = sorted(code_kinds - kinds)
        if missing_code_kinds:
            raise AssertionError(f"missing code artifact kinds: {', '.join(missing_code_kinds)}")

    print(f"readability validation passed: {len(embedded)} embedded artifacts, {len(kinds)} kinds")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
