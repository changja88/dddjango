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
    candidate = fenced.group(1) if fenced else text.strip()
    try:
        value = json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Could not parse JSON object: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit("JSON payload must be an object")
    return value


def has_non_empty_text(value: object) -> bool:
    return bool(str(value or "").strip())


def validate_oracle_schema(oracle: dict[str, object], case_id: str) -> str | None:
    if oracle.get("caseId") != case_id:
        return "caseId mismatch"
    if oracle.get("answerOracleEvaluated") is not True:
        return "answerOracleEvaluated must be true"
    for variant_key in ("baseline", "with_dddjango"):
        variant_oracle = oracle.get(variant_key)
        if not isinstance(variant_oracle, dict):
            return f"{variant_key} must be an object"
        if not has_non_empty_text(variant_oracle.get("score")):
            return f"{variant_key}.score is required"
        if not has_non_empty_text(variant_oracle.get("verdict")):
            return f"{variant_key}.verdict is required"
        if not (
            has_non_empty_text(variant_oracle.get("evaluation"))
            or has_non_empty_text(variant_oracle.get("evaluation_summary"))
        ):
            return f"{variant_key}.evaluation is required"
    observations = oracle.get("observations")
    if not isinstance(observations, list) or not observations:
        return "observations must be a non-empty list"
    return None
