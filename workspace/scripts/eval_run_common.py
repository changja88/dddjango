#!/usr/bin/env python3
"""Shared contracts for dddjango eval run scripts."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
EVAL_ROOT = REPO_ROOT / "workspace/develop/eval"
BUCKETS = ("response", "code", "plugin", "runtime", "source", "workflow")
VARIANTS = ("baseline", "with-dddjango")
ALLOWED_ORACLE_VERDICTS = {
    "pass",
    "partial",
    "pass-limited",
    "pass-control",
    "fail",
    "blocked",
}


@dataclass(frozen=True)
class BucketPaths:
    bucket: str
    root: Path
    public_cases_dir: Path
    answer_dir: Path
    runs_dir: Path


def bucket_paths(bucket: str) -> BucketPaths:
    if bucket not in BUCKETS:
        raise SystemExit(f"Unknown bucket: {bucket}")
    root = EVAL_ROOT / bucket
    return BucketPaths(
        bucket=bucket,
        root=root,
        public_cases_dir=root / "cases/plugin/public",
        answer_dir=root / "answer",
        runs_dir=root / "runs",
    )


def selected_case_paths(bucket: str, selected: list[str] | None = None) -> list[Path]:
    paths = sorted(bucket_paths(bucket).public_cases_dir.glob("case-*.md"))
    if not selected:
        if not paths:
            raise SystemExit(f"No public cases found for bucket: {bucket}")
        return paths
    wanted = set(selected)
    found = {path.stem for path in paths}
    missing = sorted(wanted - found)
    if missing:
        raise SystemExit(f"Unknown case id(s) for {bucket}: {', '.join(missing)}")
    return [path for path in paths if path.stem in wanted]


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def extract_json_object(text: str) -> dict[str, Any]:
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    candidates = [fenced.group(1)] if fenced else []
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace > first_brace:
        candidates.append(text[first_brace : last_brace + 1])
    candidates.append(text.strip())
    for candidate in candidates:
        try:
            value = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    raise ValueError("no JSON object found")


def has_non_empty_text(value: object) -> bool:
    return bool(str(value or "").strip())


def parse_score_5(value: object) -> float | None:
    text = str(value or "").strip()
    match = re.fullmatch(
        r"(?P<value>\d+(?:\.\d+)?)\s*(?:/\s*(?P<denominator>\d+(?:\.\d+)?))?",
        text,
    )
    if not match:
        return None
    denominator = match.group("denominator")
    if denominator is not None and float(denominator) != 5.0:
        return None
    score = float(match.group("value"))
    if score < 0 or score > 5:
        return None
    return score


def oracle_score_error(value: object, label: str) -> str | None:
    text = str(value or "").strip()
    if not text:
        return f"{label}.score is required"
    match = re.fullmatch(
        r"(?P<value>\d+(?:\.\d+)?)\s*(?:/\s*(?P<denominator>\d+(?:\.\d+)?))?",
        text,
    )
    if not match:
        return f"{label}.score must be a number from 0 to 5"
    denominator = match.group("denominator")
    if denominator is not None and float(denominator) != 5.0:
        return f"{label}.score denominator must be 5"
    score = float(match.group("value"))
    if score < 0 or score > 5:
        return f"{label}.score must be between 0 and 5"
    return None


def validate_oracle_schema(oracle: dict[str, object], case_id: str) -> str | None:
    if oracle.get("caseId") != case_id:
        return "caseId mismatch"
    if oracle.get("answerOracleEvaluated") is not True:
        return "answerOracleEvaluated must be true"
    for variant_key in ("baseline", "with_dddjango"):
        variant_oracle = oracle.get(variant_key)
        if not isinstance(variant_oracle, dict):
            return f"{variant_key} must be an object"
        score_error = oracle_score_error(variant_oracle.get("score"), variant_key)
        if score_error is not None:
            return score_error
        verdict_text = str(variant_oracle.get("verdict") or "").strip()
        if not verdict_text:
            return f"{variant_key}.verdict is required"
        if verdict_text.lower() not in ALLOWED_ORACLE_VERDICTS:
            return f"{variant_key}.verdict is unsupported: {verdict_text}"
        if not (
            has_non_empty_text(variant_oracle.get("evaluation"))
            or has_non_empty_text(variant_oracle.get("evaluation_summary"))
        ):
            return f"{variant_key}.evaluation is required"
    observations = oracle.get("observations")
    if not isinstance(observations, list) or not observations:
        return "observations must be a non-empty list"
    return None
