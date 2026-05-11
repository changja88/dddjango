#!/usr/bin/env python3
"""Extract workflow subagent trace evidence from eval run artifacts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


PARSER_VERSION = 2
SOURCE_STRUCTURED_EVENTS = "structured-events"
SOURCE_STDOUT_TRANSCRIPT = "stdout-transcript"
SOURCE_UNAVAILABLE = "unavailable"
TRACE_CAPTURE_POLICY = "response-text-claims-plus-structured-events-when-available"

ROLE_NAMES = (
    "Coordinator",
    "Domain Agent",
    "Architecture Agent",
    "DB Agent",
    "API Agent",
    "Django Agent",
    "Test Agent",
    "Review Agent",
    "Integration",
)

SUBAGENT_EVENT_NAMES = {
    "spawn_agent",
    "wait_agent",
    "send_input",
    "close_agent",
    "resume_agent",
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--variant", required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--response-path", type=Path, required=True)
    parser.add_argument("--event-path", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--skipped", action="store_true")
    return parser.parse_args(argv)


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def safe_relative(run_dir: Path, path: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(run_dir.resolve(strict=False)).as_posix()
    except ValueError:
        return path.as_posix()


def iter_json_objects(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    objects: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        text = line.strip()
        if not text or not text.startswith("{"):
            continue
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            objects.append(value)
    return objects


def recursive_values(value: Any) -> list[str]:
    values: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            values.append(str(key))
            values.extend(recursive_values(item))
    elif isinstance(value, list):
        for item in value:
            values.extend(recursive_values(item))
    elif isinstance(value, (str, int, float, bool)):
        values.append(str(value))
    return values


def subagent_tool_name(value: dict[str, Any]) -> str | None:
    item = value.get("item")
    if isinstance(item, dict):
        tool = item.get("tool")
        if item.get("type") == "collab_tool_call" and isinstance(tool, str):
            return tool if tool in SUBAGENT_EVENT_NAMES else None

    for key in ("tool", "name"):
        tool = value.get(key)
        if isinstance(tool, str) and tool in SUBAGENT_EVENT_NAMES:
            return tool
    return None


def detect_source_kind(path: Path) -> str:
    if not path.is_file() or path.stat().st_size == 0:
        return SOURCE_UNAVAILABLE
    objects = iter_json_objects(path)
    if any(subagent_tool_name(item) for item in objects):
        return SOURCE_STRUCTURED_EVENTS
    return SOURCE_STDOUT_TRANSCRIPT


def split_sentences(text: str) -> list[str]:
    candidates = re.split(r"(?<=[.!?。！？])\s+|[\r\n]+", text)
    return [candidate.strip(" \t-*") for candidate in candidates if candidate.strip(" \t-*")]


def is_hypothetical_or_instruction(sentence: str) -> bool:
    lowered = sentence.lower()
    patterns = (
        r"사용했다면",
        r"사용한다면",
        r"사용 가능하면",
        r"쓸 수 있으면",
        r"가능하면",
        r"가능한 경우",
        r"가정",
        r"\bif\b.*\b(use|used|available|run|ran)\b",
        r"\bwould\b",
        r"\bshould\b",
        r"\bwhen actual subagents are used\b",
    )
    return any(re.search(pattern, lowered) for pattern in patterns)


def sentence_has_subagent_reference(sentence: str) -> bool:
    lowered = sentence.lower()
    return bool(
        re.search(
            r"subagent|sub-agent|서브\s*에이전트|에이전트|agent|domain agent|db agent|api agent|django agent|test agent|review agent",
            lowered,
        )
    )


def sentence_is_negated_or_fallback(sentence: str) -> bool:
    lowered = sentence.lower()
    return bool(
        re.search(
            r"사용하지|사용[^\n.!?。！？]{0,40}하지|실행하지|실행[^\n.!?。！？]{0,40}하지"
            r"|쓰지 않고|not used|no subagents|without subagents|sequential fallback|순차|계획만|planned only",
            lowered,
        )
    )


def sentence_has_actual_completion(sentence: str) -> bool:
    lowered = sentence.lower()
    return bool(
        re.search(
            r"검토 완료|완료했습니다|완료했|실행했습니다|실행했|사용했습니다|사용했"
            r"|\bspawned\b|\bran\b|\breviewed\b|\bcompleted\b|\bdelegated\b",
            lowered,
        )
    )


def extract_response_claims(response_text: str) -> tuple[list[str], list[str]]:
    actual_claims: list[str] = []
    fallback_claims: list[str] = []
    for sentence in split_sentences(response_text):
        if not sentence_has_subagent_reference(sentence):
            continue
        if sentence_is_negated_or_fallback(sentence):
            fallback_claims.append(sentence)
            continue
        if is_hypothetical_or_instruction(sentence):
            continue
        if sentence_has_actual_completion(sentence):
            actual_claims.append(sentence)
    return actual_claims, fallback_claims


def roles_mentioned(response_text: str) -> list[str]:
    lowered = response_text.lower()
    mentioned: list[str] = []
    for role in ROLE_NAMES:
        if role.lower() in lowered:
            mentioned.append(role)
    return mentioned


def extract_structured_events(event_path: Path) -> tuple[int, int, int, list[dict[str, Any]]]:
    spawn_ids: set[str] = set()
    wait_ids: set[str] = set()
    result_ids: set[str] = set()
    events: list[dict[str, Any]] = []
    for index, item in enumerate(iter_json_objects(event_path)):
        tool_name = subagent_tool_name(item)
        if tool_name is None:
            continue
        event_item = item.get("item")
        if isinstance(event_item, dict) and event_item.get("id"):
            event_id = str(event_item["id"])
        else:
            event_id = f"line-{index}"
        if tool_name == "spawn_agent":
            spawn_ids.add(event_id)
        if tool_name == "wait_agent":
            wait_ids.add(event_id)
            result_ids.add(event_id)
        if tool_name == "close_agent":
            result_ids.add(event_id)
        events.append(item)
    return len(spawn_ids), len(wait_ids), len(result_ids), events


def trace_status(
    *,
    skipped: bool,
    trace_capture_reliable: bool,
    spawn_event_count: int,
    wait_event_count: int,
    result_event_count: int,
    explicit_actual_claims: list[str],
    explicit_fallback_claims: list[str],
) -> str:
    if skipped:
        return "skipped"
    if trace_capture_reliable and spawn_event_count > 0 and result_event_count > 0:
        return "actual-trace"
    if trace_capture_reliable and spawn_event_count > 0:
        return "actual-trace-incomplete"
    if trace_capture_reliable and wait_event_count > 0:
        return "actual-trace"
    if explicit_fallback_claims:
        return "fallback-stated"
    if explicit_actual_claims:
        return "claim-without-reliable-trace"
    return "no-trace"


def build_trace_summary(
    *,
    case_id: str,
    variant: str,
    run_dir: Path,
    response_path: Path,
    event_path: Path,
    skipped: bool = False,
) -> dict[str, Any]:
    response = read_text(response_path)
    source_kind = detect_source_kind(event_path)
    trace_capture_reliable = source_kind == SOURCE_STRUCTURED_EVENTS
    spawn_event_count = 0
    wait_event_count = 0
    result_event_count = 0
    subagent_tool_events: list[dict[str, Any]] = []
    if trace_capture_reliable:
        (
            spawn_event_count,
            wait_event_count,
            result_event_count,
            subagent_tool_events,
        ) = extract_structured_events(event_path)
    actual_claims, fallback_claims = extract_response_claims(response)

    status = trace_status(
        skipped=skipped,
        trace_capture_reliable=trace_capture_reliable,
        spawn_event_count=spawn_event_count,
        wait_event_count=wait_event_count,
        result_event_count=result_event_count,
        explicit_actual_claims=actual_claims,
        explicit_fallback_claims=fallback_claims,
    )
    return {
        "caseId": case_id,
        "variant": variant,
        "parserVersion": PARSER_VERSION,
        "sourceKind": source_kind,
        "traceCaptureReliable": trace_capture_reliable,
        "responseSource": safe_relative(run_dir, response_path),
        "eventSource": safe_relative(run_dir, event_path),
        "spawnEventCount": spawn_event_count,
        "waitEventCount": wait_event_count,
        "resultEventCount": result_event_count,
        "subagentToolEvents": subagent_tool_events,
        "explicitActualClaims": actual_claims,
        "explicitFallbackClaims": fallback_claims,
        "rolesMentioned": roles_mentioned(response),
        "traceStatus": status,
    }


def write_trace_summary(
    *,
    output_path: Path,
    case_id: str,
    variant: str,
    run_dir: Path,
    response_path: Path,
    event_path: Path,
    skipped: bool = False,
) -> dict[str, Any]:
    summary = build_trace_summary(
        case_id=case_id,
        variant=variant,
        run_dir=run_dir,
        response_path=response_path,
        event_path=event_path,
        skipped=skipped,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    write_trace_summary(
        output_path=args.output,
        case_id=args.case_id,
        variant=args.variant,
        run_dir=args.run_dir,
        response_path=args.response_path,
        event_path=args.event_path,
        skipped=args.skipped,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
