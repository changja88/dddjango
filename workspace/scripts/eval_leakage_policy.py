#!/usr/bin/env python3
"""Shared leakage checks for eval artifacts and generated reports."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LeakageFinding:
    category: str
    path: Path


LEAKAGE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("home-directory path", re.compile(r"/Users/[^ \n\t\"'<>]+")),
    ("temporary workspace path", re.compile(r"(?<![A-Za-z0-9_.-])/(?:private/)?tmp/[^ \n\t\"'<>]+")),
    ("codex cache path", re.compile(r"(?:^|[ \n\t\"'<>])(?:/Users/[^ \n\t\"'<>]+/)?\\.codex/plugins/cache/[^ \n\t\"'<>]+")),
    ("internal eval sentinel", re.compile(r"__DDDJANGO_PRIVATE_EVAL_SENTINEL__")),
)


def scan_text_for_leakage(text: str) -> list[str]:
    return [category for category, pattern in LEAKAGE_PATTERNS if pattern.search(text)]


def scan_files_for_leakage(paths: list[Path]) -> list[LeakageFinding]:
    findings: list[LeakageFinding] = []
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        for category in scan_text_for_leakage(text):
            findings.append(LeakageFinding(category=category, path=path))
    return findings
