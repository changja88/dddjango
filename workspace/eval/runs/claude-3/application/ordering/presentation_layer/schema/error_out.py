"""RFC 9457 Problem Details 응답 스키마 (명세 §2.3·§4.5).

모든 에러 응답의 미디어 타입은 application/problem+json. 상태별 확장 필드
(409의 requested, 422의 errors[])와 503(경합 소진, Retry-After 헤더)을 OpenAPI 에
드러내기 위해 스키마로 선언한다. 실제 변환·content-type·헤더 매핑은
presentation_layer/api/problem_detail 이 담당한다.
"""
from typing import Optional

from ninja import Schema


class FieldErrorOut(Schema):
    field: str
    reason: str


class ProblemDetailOut(Schema):
    type: str
    title: str
    status: int
    detail: Optional[str] = None
    instance: Optional[str] = None


class ValidationProblemOut(ProblemDetailOut):
    """422 — 필드별 검증 실패 목록 확장 (명세 §2.3 api minor m2)."""

    errors: list[FieldErrorOut]


class OutOfStockProblemOut(ProblemDetailOut):
    """409 — 요청 수량 에코 확장 (명세 §2.3 409)."""

    requested: int


class StockContentionProblemOut(ProblemDetailOut):
    """503 — 경합 소진(일시적). Retry-After 헤더는 응답 헤더로 전달 (명세 §2.3 api M4).

    409(out-of-stock, 영구)와 type·의미를 분리한다. 확장 바디 필드는 없고
    재시도 신호는 Retry-After 헤더가 담는다.
    """
