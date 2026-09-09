"""실제 Read 추적에서 모델의 자기 보고를 도구 성공으로 오인하지 않는다."""

import unittest

from read_probe import inspect_trace


class ReadTraceTests(unittest.TestCase):
    def test_error_tool_result_is_not_final_answer_success(self):
        events = [
            {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "r", "name": "Read", "input": {"file_path": "/fixture", "offset": 1, "limit": 250}}]}},
            {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "r", "is_error": True, "content": "25000 maximum allowed tokens"}]}},
            {"type": "result", "subtype": "success", "result": "DONE"},
        ]
        result = inspect_trace(events, {"file_path": "/fixture", "offset": 1, "limit": 250})
        self.assertTrue(result["exact_one_requested_read"])
        self.assertFalse(result["read_succeeded"])
        self.assertTrue(result["read_failed"])

    def test_missing_or_different_read_is_not_success(self):
        self.assertFalse(inspect_trace([], {"file_path": "/fixture"})["read_succeeded"])
        events = [{"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "r", "name": "Read", "input": {"file_path": "/other"}}]}},
                  {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "r", "content": "text"}]}}]
        self.assertFalse(inspect_trace(events, {"file_path": "/fixture"})["read_succeeded"])

    def test_success_requires_matching_tool_result(self):
        events = [{"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "r", "name": "Read", "input": {"file_path": "/fixture"}}]}},
                  {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "r", "content": "1→실제 내용"}]}}]
        self.assertTrue(inspect_trace(events, {"file_path": "/fixture"})["read_succeeded"])


if __name__ == "__main__":
    unittest.main()
