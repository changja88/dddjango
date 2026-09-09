"""전량 Read 비교 실험 전용. 플러그인에 배포하지 않는다."""

import json
import os
import re
import selectors
import signal
import statistics
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PRIOR = ROOT.parent
sys.path.insert(0, str(PRIOR))
from experiment import grade_constructor, grade_guard, split_utf8


def line_requests(path: str, text: str, limit: int = 250) -> list[dict]:
    count = len(text.splitlines(keepends=True))
    if limit < 1:
        raise ValueError("positive line limit required")
    return [{"file_path": path, "offset": start, "limit": min(limit, count - start + 1)}
            for start in range(1, count + 1, limit)]


def split_request(request: dict) -> list[dict]:
    limit = request.get("limit", 0)
    if limit < 2:
        raise ValueError("single line or whole chunk cannot be bisected")
    left = limit // 2
    return [{**request, "limit": left},
            {**request, "offset": request["offset"] + left, "limit": limit - left}]


def validate_read_trace(events: list[dict], files: dict[str, str], roots: list[dict],
                        max_parallel: int = 4) -> dict:
    pending = {json.dumps(request, sort_keys=True) for request in roots}
    inflight: dict[str, dict] = {}
    seen_ids: set[str] = set()
    received: dict[str, set[int]] = {path: set() for path in files}
    violations: list[str] = []
    attempts, errors, peak, restored_newlines = 0, 0, 0, 0
    compacted, final_seen = False, False
    last_read_ms = None
    for event in events:
        if final_seen:
            violations.append("event_after_final")
            break
        if "compact" in str(event.get("subtype", "")).lower():
            compacted = True
        if event.get("type") == "result":
            final_seen = True
            if pending or inflight:
                violations.append("final_before_all_reads")
            continue
        for block in event.get("message", {}).get("content", []):
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_use":
                attempts += 1
                identity, request = block.get("id"), block.get("input", {})
                if block.get("name") != "Read":
                    violations.append("unexpected_tool")
                if identity in seen_ids:
                    violations.append("duplicate_tool_id")
                    continue
                seen_ids.add(identity)
                key = json.dumps(request, sort_keys=True)
                if key not in pending:
                    violations.append("unscheduled_read")
                else:
                    pending.remove(key)
                inflight[identity] = request
                peak = max(peak, len(inflight))
                if peak > max_parallel:
                    violations.append("parallel_limit_exceeded")
            elif block.get("type") == "tool_result":
                request = inflight.pop(block.get("tool_use_id"), None)
                if request is None:
                    violations.append("unmatched_tool_result")
                    continue
                last_read_ms = event.get("elapsed_ms")
                content = block.get("content", "")
                if block.get("is_error"):
                    errors += 1
                    if isinstance(content, str) and "maximum allowed tokens" in content:
                        try:
                            pending.update(json.dumps(child, sort_keys=True) for child in split_request(request))
                        except ValueError:
                            violations.append("unreturnable_single_line_or_chunk")
                    else:
                        violations.append("non_size_read_error")
                    continue
                path = request.get("file_path")
                if path not in files:
                    violations.append("unexpected_file")
                    continue
                offset = request.get("offset", 1)
                limit = request.get("limit")
                if type(offset) is not int or offset < 1 or (limit is not None and (type(limit) is not int or limit < 1)):
                    violations.append("invalid_range")
                    continue
                lines = files[path].splitlines(keepends=True)
                end = len(lines) if limit is None else offset - 1 + limit
                expected = "".join(lines[offset - 1:end])
                actual = re.sub(r"(?m)^\d+\t", "", content) if isinstance(content, str) else None
                # Read 프리플라이트: 번호 붙인 행 범위의 마지막 LF 하나는 출력 프레이밍에서 빠진다.
                # 모든 행 번호가 정확하고 다른 바이트는 전부 같은 경우에만 그 경계 구분자를 복원한다.
                numbers = [int(value) for value in re.findall(r"(?m)^(\d+)\t", content)] if isinstance(content, str) else []
                if (expected.endswith("\n") and actual == expected[:-1]
                        and numbers == list(range(offset, min(end, len(lines)) + 1))):
                    actual += "\n"
                    restored_newlines += 1
                if actual != expected:
                    violations.append("content_not_byte_exact")
                    continue
                received[path].update(range(offset - 1, min(end, len(lines))))
    expected_bytes = sum(len(text.encode()) for text in files.values())
    received_bytes = sum(len(line.encode()) for path, text in files.items()
                         for index, line in enumerate(text.splitlines(keepends=True)) if index in received[path])
    complete = expected_bytes == received_bytes
    if not final_seen:
        violations.append("missing_final_result")
    strategy_valid = not violations
    return {"all_pass": complete and strategy_valid and not compacted,
            "source_complete": complete, "strategy_valid": strategy_valid, "no_compaction": not compacted,
            "read_attempts": attempts, "read_errors": errors, "max_inflight": peak,
            "expected_bytes": expected_bytes, "received_bytes": received_bytes,
            "boundary_newlines_restored": restored_newlines,
            "last_read_ms": last_read_ms, "violations": sorted(set(violations))}


def retain_event(event: dict, elapsed_ms: float) -> dict:
    kept = {key: value for key, value in event.items() if key not in {"message", "thinking", "signature"}}
    if "message" in event:
        message = event["message"]
        kept["message"] = {key: value for key, value in message.items() if key != "content"}
        kept["message"]["content"] = [block for block in message.get("content", [])
                                      if isinstance(block, dict) and block.get("type") in {"text", "tool_use", "tool_result"}]
    kept["elapsed_ms"] = elapsed_ms
    return kept


def grade_tasks(answer: dict) -> dict:
    guard = answer.get("guard", {})
    constructor = answer.get("constructor", {})
    guard_grade = grade_guard(guard.get("code", "") if isinstance(guard, dict) else "", allow_replace=True)
    constructor_grade = grade_constructor(constructor if isinstance(constructor, dict) else {})
    return {"all_pass": guard_grade["all_pass"] and constructor_grade["all_pass"],
            "passed_checks": len(guard_grade["passed"]) + len(constructor_grade["passed"]),
            "guard": guard_grade, "constructor": constructor_grade}


def summarize_rows(rows: list[dict]) -> dict:
    groups = {}
    for arm in ["original", "chunked"]:
        attempts = [row for row in rows if row["arm"] == arm]
        completed = [row for row in attempts if row["runtime_valid"] and row["trace"]["all_pass"] and row["grade"]["all_pass"]]
        groups[arm] = {"attempted": len(attempts), "completed": len(completed),
                       "median_total_ms": statistics.median(row["total_ms"] for row in completed) if completed else None,
                       "all_attempt_total_ms": [row["total_ms"] for row in attempts]}
    eligible = all(groups[arm]["attempted"] == 3 and groups[arm]["completed"] == 3 for arm in groups)
    reduction = ((1 - groups["chunked"]["median_total_ms"] / groups["original"]["median_total_ms"]) * 100
                 if eligible else None)
    return {"groups": groups, "all_six_valid_complete": eligible, "reduction_percent": reduction}


def prepare_trial_inputs(arm: str, source: str, directory: Path) -> dict:
    started = time.perf_counter()
    if arm not in {"original", "chunked"}:
        raise ValueError("unknown reading arm")
    directory.mkdir(parents=True, exist_ok=True)
    pieces = [source] if arm == "original" else split_utf8(source, 16000)
    files, mapping = {}, []
    prefix = ""
    for number, piece in enumerate(pieces):
        path = (directory / ("original.md" if arm == "original" else f"{number:03}.txt")).resolve()
        if path.exists() and path.read_bytes() != piece.encode():
            raise ValueError("refusing to overwrite a changed experiment input")
        path.write_bytes(piece.encode())
        files[str(path)] = piece
        mapping.append({"file_path": str(path), "original_start_line": prefix.count("\n") + 1,
                        "starts_mid_line": bool(prefix and not prefix.endswith("\n")),
                        "original_start_byte": len(prefix.encode()), "bytes": len(piece.encode()),
                        "ends_with_newline": piece.endswith("\n")})
        prefix += piece
    if "".join(files.values()).encode() != source.encode():
        raise ValueError("preparation lost source bytes")
    requests = (line_requests(next(iter(files)), source) if arm == "original"
                else [{"file_path": path} for path in files])
    return {"files": files, "requests": requests, "mapping": mapping,
            "preparation_ms": (time.perf_counter() - started) * 1000}


def capture_stream(command: list[str], prompt: str, directory: Path, timeout: float, on_event=None) -> dict:
    started = time.perf_counter()
    process = subprocess.Popen(command, cwd=directory, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, start_new_session=True)
    payload = memoryview(prompt.encode())
    written = 0
    events, parse_errors, stderr = [], [], bytearray()
    buffer = bytearray()
    timed_out = False
    selection = selectors.DefaultSelector()
    selection.register(process.stdout, selectors.EVENT_READ, "stdout")
    selection.register(process.stderr, selectors.EVENT_READ, "stderr")
    if payload:
        os.set_blocking(process.stdin.fileno(), False)
        selection.register(process.stdin, selectors.EVENT_WRITE, "stdin")
    else:
        process.stdin.close()
    try:
        while selection.get_map():
            if time.perf_counter() - started >= timeout and not timed_out:
                timed_out = True
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            for key, _ in selection.select(.1):
                if key.data == "stdin":
                    try:
                        written += os.write(process.stdin.fileno(), payload[written:written + 16384])
                    except BlockingIOError:
                        continue
                    except BrokenPipeError:
                        written = len(payload)
                    if written == len(payload):
                        selection.unregister(process.stdin)
                        process.stdin.close()
                    continue
                data = os.read(key.fileobj.fileno(), 65536)
                if not data:
                    selection.unregister(key.fileobj)
                    continue
                if key.data == "stderr":
                    stderr.extend(data)
                    continue
                buffer.extend(data)
                while b"\n" in buffer:
                    line, _, remainder = buffer.partition(b"\n")
                    buffer = bytearray(remainder)
                    if not line.strip():
                        continue
                    try:
                        event = json.loads(line)
                        if not isinstance(event, dict):
                            raise ValueError("event must be object")
                        kept = retain_event(event, (time.perf_counter() - started) * 1000)
                        events.append(kept)
                        if on_event is not None:
                            on_event(kept)
                    except (ValueError, UnicodeDecodeError) as error:
                        parse_errors.append(str(error))
        exit_code = process.wait(timeout=10)
    finally:
        selection.close()
        if not process.stdin.closed:
            process.stdin.close()
        process.stdout.close()
        process.stderr.close()
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
    if buffer.strip():
        parse_errors.append("unterminated JSON event")
    return {"events": events, "exit_code": exit_code, "wall_ms": (time.perf_counter() - started) * 1000,
            "timed_out": timed_out, "parse_errors": parse_errors, "stderr": stderr.decode(errors="replace")}
