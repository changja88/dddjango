#!/usr/bin/env python3
"""Shared run identity helpers for eval scripts."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


BUCKETS = ("response", "code", "plugin", "runtime", "source", "workflow")
SCOPE_CHOICES = ("full", "targeted", "adjacent", "rerun", "manual")
RUN_META_FILENAME = "RUN_META.json"
TOPIC_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RUN_ID_PATTERN = re.compile(
    r"^(?P<date>\d{8})-(?P<time>\d{6})-(?P<bucket>"
    + "|".join(BUCKETS)
    + r")-try(?P<try_number>\d{2})-(?P<scope>"
    + "|".join(SCOPE_CHOICES)
    + r")-(?P<topic>[a-z0-9]+(?:-[a-z0-9]+)*)$"
)


@dataclass(frozen=True)
class RunIdentity:
    run_id: str
    stamp: str
    bucket: str
    try_number: int
    scope: str
    topic: str
    created_at: str


def now_kst() -> datetime:
    return datetime.now(ZoneInfo("Asia/Seoul"))


def timestamp_text(stamp: datetime) -> str:
    return stamp.astimezone(ZoneInfo("Asia/Seoul")).strftime("%Y%m%d-%H%M%S")


def parse_created_at(stamp: str) -> str:
    parsed = datetime.strptime(stamp, "%Y%m%d-%H%M%S").replace(tzinfo=ZoneInfo("Asia/Seoul"))
    return parsed.isoformat(timespec="seconds")


def validate_topic(topic: str) -> str:
    if not TOPIC_PATTERN.fullmatch(topic):
        raise SystemExit(f"Invalid topic: {topic}")
    return topic


def validate_try_number(try_number: int) -> int:
    if isinstance(try_number, bool) or not isinstance(try_number, int):
        raise SystemExit(f"Invalid try number: {try_number}")
    if try_number < 1 or try_number > 99:
        raise SystemExit(f"Invalid try number: {try_number}")
    return try_number


def build_run_id(
    *,
    bucket: str,
    try_number: int,
    scope: str,
    topic: str,
    created_at: datetime | None = None,
) -> str:
    if bucket not in BUCKETS:
        raise SystemExit(f"Unknown bucket: {bucket}")
    if scope not in SCOPE_CHOICES:
        raise SystemExit(f"Unknown scope: {scope}")
    try_value = validate_try_number(try_number)
    topic_value = validate_topic(topic)
    stamp_value = created_at if created_at is not None else now_kst()
    return f"{timestamp_text(stamp_value)}-{bucket}-try{try_value:02d}-{scope}-{topic_value}"


def parse_run_id(run_id: str) -> RunIdentity:
    if not run_id or "/" in run_id or ".." in run_id:
        raise SystemExit(f"Invalid run id: {run_id}")
    match = RUN_ID_PATTERN.fullmatch(run_id)
    if not match:
        raise SystemExit(f"Invalid run id: {run_id}")
    try_number = int(match.group("try_number"))
    stamp = f"{match.group('date')}-{match.group('time')}"
    try:
        created_at = parse_created_at(stamp)
    except ValueError as exc:
        raise SystemExit(f"Invalid run id: {run_id}") from exc
    return RunIdentity(
        run_id=run_id,
        stamp=stamp,
        bucket=match.group("bucket"),
        try_number=try_number,
        scope=match.group("scope"),
        topic=match.group("topic"),
        created_at=created_at,
    )


def validate_production_run_id(run_id: str) -> RunIdentity:
    return parse_run_id(run_id)


def build_run_meta(
    *,
    run_id: str,
    lv_up_analysis: str = "",
    lv_up_plan: str = "",
) -> dict[str, object]:
    identity = parse_run_id(run_id)
    return {
        "schema_version": 1,
        "run_id": identity.run_id,
        "stamp": identity.stamp,
        "bucket": identity.bucket,
        "try_number": identity.try_number,
        "scope": identity.scope,
        "topic": identity.topic,
        "created_at": identity.created_at,
        "lv_up_analysis": lv_up_analysis,
        "lv_up_plan": lv_up_plan,
    }


def write_run_meta(
    run_dir: Path,
    *,
    run_id: str,
    lv_up_analysis: str = "",
    lv_up_plan: str = "",
) -> dict[str, object]:
    meta = build_run_meta(
        run_id=run_id,
        lv_up_analysis=lv_up_analysis,
        lv_up_plan=lv_up_plan,
    )
    run_dir.mkdir(parents=True, exist_ok=True)
    meta_path = run_dir / RUN_META_FILENAME
    meta_path.write_text(
        json.dumps(meta, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return meta


def load_run_meta(run_dir: Path) -> dict[str, object]:
    meta_path = run_dir / RUN_META_FILENAME
    return json.loads(meta_path.read_text(encoding="utf-8"))


def _load_meta_for_validation(run_dir: Path) -> tuple[object, list[str]]:
    meta_path = run_dir / RUN_META_FILENAME
    try:
        payload = json.loads(meta_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, [f"{RUN_META_FILENAME} is missing"]
    except json.JSONDecodeError as error:
        return None, [f"{RUN_META_FILENAME} is not valid JSON: {error.msg}"]
    return payload, []


def validate_run_meta(run_dir: Path) -> list[str]:
    run_id = run_dir.name
    try:
        identity = parse_run_id(run_id)
    except SystemExit:
        return [f"Invalid run id: {run_id}"]

    run_meta, errors = _load_meta_for_validation(run_dir)
    if errors:
        return errors
    if not isinstance(run_meta, dict):
        return [f"{RUN_META_FILENAME} must be a JSON object"]

    problems: list[str] = []
    if run_meta.get("run_id") != run_id:
        problems.append(f"{RUN_META_FILENAME} run_id must match directory run id: {run_id}")
    if run_meta.get("stamp") != identity.stamp:
        problems.append(f"{RUN_META_FILENAME} stamp must match run id stamp: {identity.stamp}")
    if run_meta.get("bucket") != identity.bucket:
        problems.append(f"{RUN_META_FILENAME} bucket must match run id bucket: {identity.bucket}")
    if run_meta.get("try_number") != identity.try_number:
        problems.append(
            f"{RUN_META_FILENAME} try_number must match run id try_number: {identity.try_number}"
        )
    if run_meta.get("scope") != identity.scope:
        problems.append(f"{RUN_META_FILENAME} scope must match run id scope: {identity.scope}")
    if run_meta.get("topic") != identity.topic:
        problems.append(f"{RUN_META_FILENAME} topic must match run id topic: {identity.topic}")
    if run_meta.get("created_at") != identity.created_at:
        problems.append(
            f"{RUN_META_FILENAME} created_at must match run id created_at: {identity.created_at}"
        )
    if run_meta.get("schema_version") != 1:
        problems.append(f"{RUN_META_FILENAME} schema_version must be 1")
    for key in ("lv_up_analysis", "lv_up_plan"):
        value = run_meta.get(key)
        if not isinstance(value, str):
            problems.append(f"{RUN_META_FILENAME} {key} must be a string")
    return problems


def has_answer_oracle_evaluation(run_dir: Path) -> bool:
    return any((run_dir / "raw").glob("*-answer-oracle-evaluation.json"))


def exit_artifacts_are_clean(run_dir: Path) -> bool:
    exit_artifacts = [
        path
        for path in (run_dir / "raw").glob("*-exit.txt")
        if not path.name.endswith("-answer-oracle-evaluation-exit.txt")
    ]
    if not exit_artifacts:
        return False
    return all(
        exit_artifact.read_text(encoding="utf-8").strip() == "0"
        for exit_artifact in exit_artifacts
    )
