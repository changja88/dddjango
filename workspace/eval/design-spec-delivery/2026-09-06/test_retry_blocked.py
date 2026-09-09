"""한도 거부만 한 번 재시도하고 원래 품질 실패를 갈아 끼우지 않는다."""

import unittest

from retry_blocked import retry_candidates, reconcile_trials


def original(name, started, *, blocked=True):
    return {"trial": name, "case": "guard", "arm": "full", "repeat": 3,
            "started_utc": started, "prompt_sha256": "same", "command": ["claude", "-p"],
            "error": "model/harness error" if blocked else None,
            "grade": None if blocked else {"all_pass": False},
            "response": {"api_error_status": 429, "modelUsage": {}} if blocked else {"modelUsage": {"model": {}}}}


class RetryTests(unittest.TestCase):
    def test_only_unretried_quota_errors_are_selected_in_original_order(self):
        rows = [original("later", "02"), original("earlier", "01"), original("quality_failure", "03", blocked=False)]
        self.assertEqual([r["trial"] for r in retry_candidates(rows, {"later"})], ["earlier"])

    def test_model_executed_and_non_quota_errors_are_not_retried(self):
        executed = original("executed", "01")
        executed["response"]["modelUsage"] = {"model": {}}
        server = original("server", "02")
        server["response"]["api_error_status"] = 500
        self.assertEqual(retry_candidates([executed, server], set()), [])

    def test_retry_replaces_unexecuted_slot_without_double_counting(self):
        blocked = original("slot", "01")
        retry = {**blocked, "retry_of": "slot", "error": None, "grade": {"all_pass": True}}
        rows = reconcile_trials([blocked], [retry])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["grade"], {"all_pass": True})
        self.assertIsNone(blocked["grade"])

    def test_quality_failure_cannot_be_replaced_by_success(self):
        failed = original("slot", "01", blocked=False)
        with self.assertRaises(ValueError):
            reconcile_trials([failed], [{**failed, "retry_of": "slot", "grade": {"all_pass": True}}])

    def test_duplicate_or_changed_input_retry_is_rejected(self):
        blocked = original("slot", "01")
        retry = {**blocked, "retry_of": "slot"}
        with self.assertRaises(ValueError):
            reconcile_trials([blocked], [retry, retry])
        with self.assertRaises(ValueError):
            reconcile_trials([blocked], [{**retry, "prompt_sha256": "changed"}])

    def test_unknown_retry_does_not_create_a_new_trial(self):
        with self.assertRaises(ValueError):
            reconcile_trials([], [{**original("unknown", "01"), "retry_of": "unknown"}])


if __name__ == "__main__":
    unittest.main()
