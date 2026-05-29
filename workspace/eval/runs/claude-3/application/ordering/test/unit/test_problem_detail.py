"""Problem Details 변환 단위 테스트 (안쪽 루프).

근거: 설계 명세 §2.3(RFC 9457 에러표·type/필드/상태코드)·§4.5(에러 표면).
표현 계층의 순수 변환 로직만 검증한다 — 검증 에러 매핑·400/415 구분·type URI 구성.
전체 HTTP 계약은 인수 테스트가 덮으므로 여기서는 매핑 엣지만 본다.
"""
from django.test import SimpleTestCase

from application.ordering.presentation_layer.api.problem_detail import (
    PROBLEM_CONTENT_TYPE,
    RETRY_AFTER_SECONDS,
    build_problem_body,
    build_stock_contention_response,
    format_validation_errors,
    problem_type_uri,
)


class ProblemTypeUriTest(SimpleTestCase):
    """type 은 /problems/<slug> 안정 URI (명세 §2.3 api M2)."""

    def test_prefixes_slug_with_problems_base(self) -> None:
        self.assertEqual(problem_type_uri("out-of-stock"), "/problems/out-of-stock")


class BuildProblemBodyTest(SimpleTestCase):
    """problem+json 바디는 type·title·status 를 담고, 확장 필드를 병합한다."""

    def test_carries_core_fields(self) -> None:
        body = build_problem_body(slug="bad-request", title="Malformed request.", status=400)

        self.assertEqual(body["type"], "/problems/bad-request")
        self.assertEqual(body["title"], "Malformed request.")
        self.assertEqual(body["status"], 400)

    def test_merges_extension_fields(self) -> None:
        body = build_problem_body(
            slug="out-of-stock",
            title="Insufficient stock.",
            status=409,
            extra={"requested": 5},
        )

        # 확장 필드가 코어 필드와 함께 노출된다(명세 §2.3 409 requested 에코).
        self.assertEqual(body["requested"], 5)
        self.assertEqual(body["status"], 409)


class FormatValidationErrorsTest(SimpleTestCase):
    """Ninja/Pydantic 검증 에러를 errors:[{field, reason}] 로 매핑 (명세 §2.3 api minor m2)."""

    def test_maps_loc_to_field_and_msg_to_reason(self) -> None:
        ninja_errors = [
            {"loc": ("body", "quantity"), "msg": "Input should be greater than or equal to 1"}
        ]

        errors = format_validation_errors(ninja_errors)

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["field"], "quantity")
        self.assertEqual(errors[0]["reason"], "Input should be greater than or equal to 1")

    def test_drops_source_prefix_and_joins_nested_path(self) -> None:
        ninja_errors = [{"loc": ("body", "payload", "quantity"), "msg": "Field required"}]

        errors = format_validation_errors(ninja_errors)

        self.assertEqual(errors[0]["field"], "payload.quantity")

    def test_falls_back_to_source_when_no_field_path(self) -> None:
        # loc 에 필드 경로가 없으면(소스만) 소스 라벨을 field 로 둔다.
        errors = format_validation_errors([{"loc": ("body",), "msg": "bad"}])

        self.assertEqual(errors[0]["field"], "body")


class StockContentionResponseTest(SimpleTestCase):
    """503 경합 소진 응답: type·status·Retry-After·problem+json (명세 §2.3 api M4)."""

    def test_returns_503_problem_with_stock_contention_type(self) -> None:
        response = build_stock_contention_response(detail="경합 소진")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response["Content-Type"], PROBLEM_CONTENT_TYPE)

        import json

        body = json.loads(response.content)
        # 503 은 일시적 경합 소진 — type 을 409(out-of-stock)와 의미 분리(명세 §2.3).
        self.assertEqual(body["type"], "/problems/stock-contention")
        self.assertEqual(body["status"], 503)
        self.assertEqual(body["detail"], "경합 소진")

    def test_carries_retry_after_header(self) -> None:
        # 503 + Retry-After: 클라이언트에 재시도 신호(명세 §2.3·§5-8).
        response = build_stock_contention_response(detail="경합 소진")

        self.assertIn("Retry-After", response)
        self.assertEqual(response["Retry-After"], str(RETRY_AFTER_SECONDS))
