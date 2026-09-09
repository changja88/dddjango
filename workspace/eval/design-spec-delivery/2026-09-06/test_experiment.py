"""실험 결과를 왜곡할 수 있는 전송·검색·채점 결함의 회귀 테스트."""

import unittest

from experiment import (
    check_index, closure, coverage, grade_constructor, grade_guard,
    make_units, rank_units, select_budget, split_utf8,
)


GOOD_GUARD = '''def render_situation(templates, situation, subject):
    if situation not in templates:
        raise InvalidSpeechSituation()
    line = templates[situation]
    if "{subject}" in line and (subject is None or not subject.strip()):
        raise InvalidSpeechSituation()
    return line.format(subject="" if subject is None else subject)
'''


class TransmissionTests(unittest.TestCase):
    def test_utf8_boundaries_preserve_korean_emoji_and_newlines(self):
        original = "가😀\n| 표 | 값 |\n```py\nx = 1\n```\n"
        chunks = split_utf8(original, 7)
        self.assertEqual("".join(chunks), original)
        self.assertTrue(all(0 < len(c.encode()) <= 7 for c in chunks))

    def test_unrepresentable_codepoint_is_rejected_not_lost(self):
        with self.assertRaises(ValueError):
            split_utf8("😀", 3)

    def test_code_fence_heading_does_not_pollute_metadata(self):
        units = make_units("## 1. 실제\n```py\n# 9. 코드 안\n```\n계약\n")
        self.assertTrue(units, "source lines must produce addressable units")
        self.assertEqual(units[-1]["line"], 5)
        self.assertEqual(units[-1]["heading"], "1. 실제")

    def test_search_finds_body_and_context_and_budget_never_cuts_a_unit(self):
        units = [{"id": "heading", "line": 1, "text": "## 1. target\n", "heading": "1. target"},
                 {"id": "needle", "line": 2, "text": "needle\n", "heading": "1. target"},
                 {"id": "other", "line": 3, "text": "other value\n", "heading": "1. target"}]
        ranked = rank_units(units, "needle")
        self.assertTrue(ranked, "matching body must be returned")
        self.assertEqual(ranked[0], units[1]["id"])
        selected = select_budget(units, ranked, 7)
        self.assertEqual([u["text"] for u in selected], ["needle\n"])
        self.assertIn(units[1]["id"], rank_units(units, "target", True))

    def test_reference_cycles_terminate_and_preserve_bridge(self):
        self.assertEqual(closure(["A"], [("A", "B"), ("B", "C"), ("C", "A")]), ["A", "B", "C"])

    def test_stale_and_dangling_targets_are_rejected(self):
        with self.assertRaises(ValueError):
            check_index("old", "new", ["A"], [])
        with self.assertRaises(ValueError):
            check_index("same", "same", ["A"], [("A", "missing")])
        check_index("same", "same", ["A", "B"], [("A", "B")])

    def test_multifactor_obligation_requires_all_supporting_lines(self):
        obligations = [{"id": "both", "supports": [[1, 3], [9]]}]
        self.assertFalse(coverage([{"line": 1}], obligations)["all_pass"])
        self.assertTrue(coverage([{"line": 1}, {"line": 3}], obligations)["all_pass"])
        self.assertTrue(coverage([{"line": 9}], obligations)["all_pass"])


class GradingTests(unittest.TestCase):
    def test_real_guard_accepts_valid_and_rejects_absent_subject(self):
        self.assertTrue(grade_guard(GOOD_GUARD)["all_pass"])

    def test_guard_exception_message_style_does_not_change_grade(self):
        with_message = GOOD_GUARD.replace("raise InvalidSpeechSituation()", 'raise InvalidSpeechSituation(f"invalid: {situation}")')
        self.assertTrue(grade_guard(with_message)["all_pass"])

    def test_explicit_replace_adjudication_preserves_original_grade_and_behavior_checks(self):
        with_replace = GOOD_GUARD.replace('line.format(subject="" if subject is None else subject)', 'line.replace("{subject}", "" if subject is None else subject)')
        self.assertFalse(grade_guard(with_replace)["all_pass"])
        self.assertTrue(grade_guard(with_replace, allow_replace=True)["all_pass"])
        missing_guard = with_replace.replace('if "{subject}" in line and (subject is None or not subject.strip()):', 'if False:')
        self.assertFalse(grade_guard(missing_guard, allow_replace=True)["all_pass"])
        self.assertFalse(grade_guard('def render_situation(templates, situation, subject):\n    return subject.__class__\n', allow_replace=True)["all_pass"])

    def test_missing_guard_and_copied_situation_set_are_detected(self):
        missing = 'def render_situation(templates, situation, subject):\n    return templates[situation].format(subject="" if subject is None else subject)\n'
        self.assertFalse(grade_guard(missing)["all_pass"])
        copied = GOOD_GUARD.replace('"{subject}" in line', 'situation == "PROFILE_INPUT_REQUEST"')
        self.assertFalse(grade_guard(copied)["all_pass"])

    def test_untrusted_code_cannot_import_or_reach_python_introspection(self):
        self.assertFalse(grade_guard('import os\n' + GOOD_GUARD)["all_pass"])
        self.assertFalse(grade_guard('def render_situation(templates, situation, subject):\n    return subject.__class__\n')["all_pass"])

    def test_constructor_grader_rejects_missing_fields_and_wrong_test_obligation(self):
        self.assertFalse(grade_constructor({})["all_pass"])
        answer = {"request_required": True, "request_nullable": True,
                  "loader_argument": "request=request", "callers_first": True,
                  "new_test_cases_required": False, "new_assertions_required": False,
                  "prepared_file_count": 6, "prepared_constructor_calls": 7,
                  "remaining_production_change": "remove_default_only"}
        self.assertTrue(grade_constructor(answer)["all_pass"])
        answer["loader_argument"] = "request = request"
        self.assertTrue(grade_constructor(answer)["all_pass"])
        answer["loader_argument"] = "request=None"
        self.assertFalse(grade_constructor(answer)["all_pass"])
        answer["loader_argument"] = "request=request"
        answer["new_test_cases_required"] = True
        self.assertFalse(grade_constructor(answer)["all_pass"])


if __name__ == "__main__":
    unittest.main()
