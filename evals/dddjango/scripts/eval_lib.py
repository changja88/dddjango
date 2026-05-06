#!/usr/bin/env python3
"""Shared helpers for the dddjango purpose-fit evaluation."""

from __future__ import annotations

import html
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EVAL_ROOT = ROOT / "evals/dddjango"
WORKSPACE_ROOT = ROOT / "workspace/codex-eval/purpose-fit"
VARIANTS = ("without-dddjango", "with-dddjango")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def load_dimensions() -> dict[str, dict[str, Any]]:
    return read_json(EVAL_ROOT / "rubrics/dimensions.json")


def load_gates() -> dict[str, dict[str, Any]]:
    return read_json(EVAL_ROOT / "rubrics/gates.json")


def load_release_gates() -> dict[str, dict[str, Any]]:
    return read_json(EVAL_ROOT / "rubrics/release-gates.json")


def load_case_suites() -> list[dict[str, Any]]:
    return [read_json(path) for path in sorted((EVAL_ROOT / "cases").glob("*.json"))]


def load_cases(suite_name: str | None = None) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for suite in load_case_suites():
        if suite_name and suite.get("suite") != suite_name:
            continue
        for case in suite.get("cases", []):
            item = dict(case)
            item["suite"] = suite.get("suite")
            cases.append(item)
    return cases


def find_case(case_id: str) -> dict[str, Any]:
    for case in load_cases():
        if case["id"] == case_id:
            return case
    raise ValueError(f"Unknown case id: {case_id}")


def make_run_id() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S-%f")


def latest_run_dir() -> Path:
    if not WORKSPACE_ROOT.exists():
        raise FileNotFoundError("No purpose-fit evaluation runs exist.")
    runs = sorted(
        path for path in WORKSPACE_ROOT.iterdir()
        if path.is_dir()
        and not path.name.startswith("calibration-")
        and (path / "metadata.json").exists()
    )
    if not runs:
        raise FileNotFoundError("No purpose-fit evaluation runs exist.")
    return runs[-1]


def run_dir_from_args(run_id: str | None, latest: bool) -> Path:
    if latest:
        return latest_run_dir()
    if not run_id:
        raise ValueError("--run-id or --latest is required")
    return WORKSPACE_ROOT / run_id


def markdown_to_html(markdown: str, *, title: str) -> str:
    escaped = html.escape(markdown)
    body = escaped.replace("\n", "<br>\n")
    return "\n".join(
        [
            "<!doctype html>",
            "<html lang=\"ko\">",
            "<head>",
            "  <meta charset=\"utf-8\">",
            f"  <title>{html.escape(title)}</title>",
            "  <style>",
            "    body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 32px; line-height: 1.6; color: #111827; }",
            "    .artifact { max-width: 980px; }",
            "    code, pre { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }",
            "  </style>",
            "</head>",
            "<body>",
            f"  <main class=\"artifact\"><h1>{html.escape(title)}</h1><p>{body}</p></main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def contains_hangul(text: str) -> bool:
    return bool(re.search(r"[가-힣]", text))


def hangul_ratio(text: str) -> float:
    letters = re.findall(r"[A-Za-z가-힣]", text)
    if not letters:
        return 0.0
    hangul = [letter for letter in letters if re.match(r"[가-힣]", letter)]
    return len(hangul) / len(letters)


def prose_text(text: str) -> str:
    """Return markdown prose with fenced code blocks removed."""
    without_fences = re.sub(r"```[\s\S]*?```", " ", text)
    without_inline_code = re.sub(r"`[^`\n]+`", " ", without_fences)
    return without_inline_code


def regex_matches(patterns: list[str], text: str) -> list[str]:
    matches: list[str] = []
    for pattern in patterns:
        if re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE):
            matches.append(pattern)
    return matches


def substring_matches(patterns: list[str], text: str) -> list[str]:
    lower = text.lower()
    return [pattern for pattern in patterns if pattern.lower() in lower]


def ordered(text: str, patterns: list[str]) -> bool:
    index = -1
    lower = text.lower()
    for pattern in patterns:
        next_index = lower.find(pattern.lower(), index + 1)
        if next_index == -1:
            return False
        index = next_index
    return True


def clamp_score(score: float) -> int:
    return max(0, min(100, round(score)))
