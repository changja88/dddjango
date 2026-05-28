"""error_out Problem Details 구성 단위 테스트 (§2.5 / §5.6).

슬라이스 B가 추가하는 400(필드 검증 errors 맵)·400(JSON 파싱 실패 detail만)·
405(Method not allowed) 본문 형태를 검증한다.
"""
from django.test import SimpleTestCase

from application.catalog.presentation_layer.schema import error_out


class InvalidRequestTest(SimpleTestCase):
    def test_필드_검증_실패는_errors_맵을_포함한다(self) -> None:
        body = error_out.invalid_request({"quantity": "must be an integer >= 1"})

        self.assertEqual(body["type"], "about:blank")
        self.assertEqual(body["title"], "Invalid request")
        self.assertEqual(body["status"], 400)
        self.assertIn("detail", body)
        self.assertEqual(body["errors"], {"quantity": "must be an integer >= 1"})


class InvalidJsonTest(SimpleTestCase):
    def test_파싱_실패는_errors를_생략하고_detail만_담는다(self) -> None:
        body = error_out.invalid_json("Request body is not valid JSON.")

        self.assertEqual(body["type"], "about:blank")
        self.assertEqual(body["title"], "Invalid request")
        self.assertEqual(body["status"], 400)
        self.assertEqual(body["detail"], "Request body is not valid JSON.")
        self.assertNotIn("errors", body)


class MethodNotAllowedTest(SimpleTestCase):
    def test_메서드_불가는_405_problem_details를_구성한다(self) -> None:
        body = error_out.method_not_allowed()

        self.assertEqual(body["type"], "about:blank")
        self.assertEqual(body["title"], "Method not allowed")
        self.assertEqual(body["status"], 405)
        self.assertIn("detail", body)
