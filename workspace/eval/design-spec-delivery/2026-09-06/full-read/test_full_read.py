"""읽기 누락·조용한 절단·전략 이탈·요약과 품질 실패를 속도 개선으로 세지 않는다."""

import unittest
import sys
import tempfile
from pathlib import Path

from full_read import (grade_tasks, line_requests, retain_event, split_request,
                       summarize_rows, validate_read_trace, prepare_trial_inputs, capture_stream)


def use(identity, request):
    return {"type": "assistant", "elapsed_ms": 10,
            "message": {"content": [{"type": "tool_use", "id": identity,
                                      "name": "Read", "input": request}]}}


def result(identity, content, error=False, elapsed=20):
    return {"type": "user", "elapsed_ms": elapsed,
            "message": {"content": [{"type": "tool_result", "tool_use_id": identity,
                                      "content": content, "is_error": error}]}}


FINAL = {"type": "result", "subtype": "success", "result": "{}", "elapsed_ms": 30}


class ReadPlanTests(unittest.TestCase):
    def test_initial_line_windows_cover_tail_without_overlap(self):
        self.assertEqual(line_requests("/doc", "가\n나\n다\n라\n마", 2), [
            {"file_path": "/doc", "offset": 1, "limit": 2},
            {"file_path": "/doc", "offset": 3, "limit": 2},
            {"file_path": "/doc", "offset": 5, "limit": 1}])

    def test_error_bisection_covers_odd_range_and_cannot_split_single_line(self):
        self.assertEqual(split_request({"file_path": "/doc", "offset": 8, "limit": 5}), [
            {"file_path": "/doc", "offset": 8, "limit": 2},
            {"file_path": "/doc", "offset": 10, "limit": 3}])
        with self.assertRaises(ValueError):
            split_request({"file_path": "/doc", "offset": 8, "limit": 1})


class TraceTests(unittest.TestCase):
    def test_retried_ranges_require_every_original_byte_before_final(self):
        root = {"file_path": "/doc", "offset": 1, "limit": 3}
        a = {"file_path": "/doc", "offset": 1, "limit": 1}
        b = {"file_path": "/doc", "offset": 2, "limit": 2}
        events = [use("root", root), result("root", "File content exceeds maximum allowed tokens", True),
                  use("a", a), use("b", b), result("b", "2\t나\n3\t다", elapsed=24),
                  result("a", "1\t가\n", elapsed=25), FINAL]
        observed = validate_read_trace(events, {"/doc": "가\n나\n다"}, [root])
        self.assertTrue(observed["all_pass"])
        self.assertEqual(observed["read_attempts"], 3)
        self.assertEqual(observed["read_errors"], 1)
        self.assertEqual(observed["received_bytes"], 11)
        self.assertEqual(observed["last_read_ms"], 25)
        self.assertFalse(validate_read_trace(events[:-2] + [FINAL], {"/doc": "가\n나\n다"}, [root])["all_pass"])

    def test_chunk_contents_and_mid_line_boundaries_are_preserved(self):
        a, b = {"file_path": "/a"}, {"file_path": "/b"}
        events = [use("a", a), use("b", b), result("a", "1\t긴 "),
                  result("b", "1\t문장\n2\t끝"), FINAL]
        observed = validate_read_trace(events, {"/a": "긴 ", "/b": "문장\n끝"}, [a, b])
        self.assertTrue(observed["all_pass"])
        self.assertEqual(observed["received_bytes"], 14)

    def test_success_flag_does_not_hide_silent_truncation(self):
        request = {"file_path": "/doc"}
        events = [use("a", request), result("a", "1\t앞"), FINAL]
        observed = validate_read_trace(events, {"/doc": "앞뒤"}, [request])
        self.assertFalse(observed["source_complete"])
        self.assertIn("content_not_byte_exact", observed["violations"])

    def test_numbered_range_may_omit_only_its_terminal_line_separator(self):
        request = {"file_path": "/doc", "offset": 1, "limit": 2}
        events = [use("a", request), result("a", "1\tA\n2\tB"), FINAL]
        observed = validate_read_trace(events, {"/doc": "A\nB\n"}, [request])
        self.assertTrue(observed["all_pass"])
        self.assertEqual(observed["boundary_newlines_restored"], 1)
        self.assertEqual(observed["received_bytes"], 4)
        for content in ["1\tA\n2\t", "1\tA\n9\tB", "A\nB"]:
            with self.subTest(content=content):
                self.assertFalse(validate_read_trace([use("a", request), result("a", content), FINAL],
                                                     {"/doc": "A\nB\n"}, [request])["all_pass"])

    def test_reading_unscheduled_range_or_path_is_protocol_failure(self):
        root = {"file_path": "/doc", "offset": 1, "limit": 2}
        for request in [{"file_path": "/doc"}, {"file_path": "/outside"}]:
            with self.subTest(request=request):
                observed = validate_read_trace([use("a", request), result("a", "1\tA\n2\tB"), FINAL],
                                               {"/doc": "A\nB"}, [root])
                self.assertFalse(observed["strategy_valid"])

    def test_too_many_outstanding_reads_and_duplicate_results_are_rejected(self):
        roots = [{"file_path": f"/{i}"} for i in range(5)]
        files = {f"/{i}": "A" for i in range(5)}
        events = [use(str(i), request) for i, request in enumerate(roots)]
        events += [result(str(i), "1\tA") for i in range(5)] + [FINAL]
        self.assertIn("parallel_limit_exceeded", validate_read_trace(events, files, roots)["violations"])
        duplicated = [use("a", roots[0]), result("a", "1\tA"), result("a", "1\tA"), FINAL]
        self.assertFalse(validate_read_trace(duplicated, {"/0": "A"}, roots[:1])["strategy_valid"])

    def test_compaction_disqualifies_lossless_no_summary_condition(self):
        request = {"file_path": "/doc"}
        events = [use("a", request), result("a", "1\tA"),
                  {"type": "system", "subtype": "compact_boundary"}, FINAL]
        observed = validate_read_trace(events, {"/doc": "A"}, [request])
        self.assertTrue(observed["source_complete"])
        self.assertFalse(observed["no_compaction"])
        self.assertFalse(observed["all_pass"])

    def test_final_before_last_result_cannot_be_made_complete_by_later_events(self):
        request = {"file_path": "/doc"}
        events = [use("a", request), FINAL, result("a", "1\tA")]
        self.assertFalse(validate_read_trace(events, {"/doc": "A"}, [request])["all_pass"])

    def test_retention_drops_thinking_and_keeps_tools_and_metrics(self):
        event = {"type": "assistant", "message": {"content": [
            {"type": "thinking", "thinking": "private", "signature": "secret"},
            {"type": "tool_use", "id": "a", "name": "Read", "input": {"file_path": "/doc"}}]}}
        kept = retain_event(event, 12)
        self.assertIn("message", kept)
        self.assertEqual(len(kept["message"]["content"]), 1)
        self.assertEqual(kept["message"]["content"][0]["type"], "tool_use")
        self.assertEqual(kept["elapsed_ms"], 12)


class TaskAndSummaryTests(unittest.TestCase):
    def test_both_original_task_contracts_are_required(self):
        answer = {"guard": {"code": "def render_situation(templates, situation, subject):\n"
                  "    if situation not in templates:\n        raise InvalidSpeechSituation()\n"
                  "    line = templates[situation]\n    if '{subject}' not in line:\n        return line\n"
                  "    if subject is None or not subject.strip():\n        raise InvalidSpeechSituation()\n"
                  "    return line.replace('{subject}', subject)\n"},
                  "constructor": {"request_required": True, "request_nullable": True,
                                  "loader_argument": "request=request", "callers_first": True,
                                  "new_test_cases_required": False, "new_assertions_required": False,
                                  "prepared_file_count": 6, "prepared_constructor_calls": 7,
                                  "remaining_production_change": "remove_default_only"}}
        observed = grade_tasks(answer)
        self.assertTrue(observed["all_pass"])
        self.assertEqual(observed["passed_checks"], 19)
        answer["constructor"]["request_nullable"] = False
        self.assertFalse(grade_tasks(answer)["all_pass"])
        self.assertFalse(grade_tasks({})["all_pass"])

    def test_fast_incomplete_or_wrong_answers_are_not_successful_speedups(self):
        rows = [{"arm": "original", "total_ms": 100, "wall_ms": 90, "preparation_ms": 10,
                 "trace": {"all_pass": True}, "grade": {"all_pass": True}, "runtime_valid": True},
                {"arm": "chunked", "total_ms": 1, "wall_ms": 1, "preparation_ms": 0,
                 "trace": {"all_pass": False}, "grade": {"all_pass": True}, "runtime_valid": True},
                {"arm": "chunked", "total_ms": 2, "wall_ms": 2, "preparation_ms": 0,
                 "trace": {"all_pass": True}, "grade": {"all_pass": False}, "runtime_valid": True}]
        summary = summarize_rows(rows)
        self.assertIn("groups", summary)
        self.assertEqual(summary["groups"]["chunked"]["completed"], 0)
        self.assertIsNone(summary["reduction_percent"])
        self.assertEqual(summary["groups"]["chunked"]["attempted"], 2)


class RunnerBoundaryTests(unittest.TestCase):
    def test_runtime_api_failure_stops_even_after_primary_or_auxiliary_usage(self):
        from run_full_read import MODEL, runtime_unavailable
        primary = {MODEL: {"inputTokens": 100}}
        self.assertTrue(runtime_unavailable({"modelUsage": primary, "api_error_status": 503}))
        self.assertTrue(runtime_unavailable({"modelUsage": primary, "terminal_reason": "api_error"}))
        self.assertTrue(runtime_unavailable({"modelUsage": {"claude-haiku": {"inputTokens": 100}}}))
        self.assertTrue(runtime_unavailable({}))
        self.assertFalse(runtime_unavailable({"modelUsage": primary, "subtype": "success"}))

    def test_preparation_preserves_all_bytes_and_refuses_changed_existing_input(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            text = "한" * 6000 + "\n마지막"
            chunked = prepare_trial_inputs("chunked", text, root)
            self.assertIn("files", chunked)
            self.assertEqual("".join(chunked["files"].values()), text)
            self.assertEqual(len(chunked["files"]), 2)
            self.assertEqual(chunked["mapping"][1]["original_start_line"], 1)
            self.assertTrue(chunked["mapping"][1]["starts_mid_line"])
            self.assertTrue(all(Path(p).read_text() == content for p, content in chunked["files"].items()))
            with self.assertRaises(ValueError):
                prepare_trial_inputs("chunked", "different", root)

    def test_real_subprocess_capture_sanitizes_events_and_records_nonzero_exit(self):
        command = [sys.executable, "-c", "import sys,json; sys.stdin.read(); "
                   "print(json.dumps({'type':'assistant','message':{'content':[{'type':'thinking','thinking':'private'}]}})); "
                   "print(json.dumps({'type':'result','subtype':'error_during_execution','result':'fixture error'})); sys.exit(7)"]
        with tempfile.TemporaryDirectory() as directory:
            observed = capture_stream(command, "test", Path(directory), 10)
        self.assertIn("exit_code", observed)
        self.assertEqual(observed["exit_code"], 7)
        self.assertGreater(observed["wall_ms"], 0)
        self.assertEqual(observed["events"][0]["message"]["content"], [])
        self.assertFalse(observed["timed_out"])

    def test_process_timeout_is_not_success_and_preserves_partial_events(self):
        command = [sys.executable, "-u", "-c", "import time; print('{\"type\":\"system\",\"subtype\":\"init\"}'); time.sleep(5)"]
        with tempfile.TemporaryDirectory() as directory:
            observed = capture_stream(command, "", Path(directory), .15)
        self.assertIn("timed_out", observed)
        self.assertTrue(observed["timed_out"])
        self.assertEqual(observed["events"][0]["subtype"], "init")

    def test_early_exit_during_large_stdin_is_preserved_not_raised(self):
        command = [sys.executable, "-u", "-c", "import sys; print('{\"type\":\"result\",\"result\":\"early exit\"}'); sys.exit(7)"]
        with tempfile.TemporaryDirectory() as directory:
            try:
                observed = capture_stream(command, "X" * 2000000, Path(directory), 2)
            except BrokenPipeError:
                self.fail("lost early-exit evidence during stdin write")
        self.assertEqual(observed["exit_code"], 7)
        self.assertEqual(observed["events"][0]["result"], "early exit")

    def test_timeout_covers_stdin_when_child_does_not_read_it(self):
        command = [sys.executable, "-u", "-c", "import time; print('{\"type\":\"system\"}'); time.sleep(.5)"]
        with tempfile.TemporaryDirectory() as directory:
            try:
                observed = capture_stream(command, "X" * 2000000, Path(directory), .1)
            except BrokenPipeError:
                self.fail("stdin write bypassed timeout")
        self.assertTrue(observed["timed_out"])
        self.assertLess(observed["wall_ms"], 450)


if __name__ == "__main__":
    unittest.main()
