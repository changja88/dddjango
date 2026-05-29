"""RFC 9457 Problem Details 변환 (명세 §2.3·§4.5).

도메인/응용 예외와 프레임워크 검증·파싱 에러를 application/problem+json 으로
변환하는 표현 계층 책임이다. Ninja 의 response 스키마 매핑을 우회하지 않도록
중앙 exception_handler 로 등록한다(명세 §2.1 어댑터 선택·implementation-django-ninja §6.2).

매핑(명세 §2.3 에러표):
- OutOfStock              -> 409 /problems/out-of-stock      (requested 에코)
- ProductNotFound         -> 404 /problems/product-not-found
- InvalidQuantity         -> 422 /problems/validation-error  (도메인 백스톱)
- Ninja ValidationError   -> 422 /problems/validation-error  (errors[] 확장)
- HttpError(400, 파싱)     -> 400 /problems/bad-request | 415 /problems/unsupported-media-type
  (요청 Content-Type 이 JSON 이 아니면 415, malformed JSON 이면 400 — 명세 api M1)
- StockContentionExhausted -> 503 /problems/stock-contention (Retry-After, 409 와 의미 분리 — api M4)
"""
from typing import Any, Optional

from django.http import HttpRequest, JsonResponse
from ninja import NinjaAPI
from ninja.errors import HttpError, ValidationError

from application.ordering.domain_layer.order.exception import (
    InvalidQuantity,
    OutOfStock,
    ProductNotFound,
    StockContentionExhausted,
)

PROBLEM_CONTENT_TYPE = "application/problem+json"
_PROBLEM_BASE = "/problems"

# 503 경합 소진 시 클라이언트 재시도 대기 힌트(초). 일시적 경합이라 짧게 둔다.
RETRY_AFTER_SECONDS = 1

# Ninja 검증 에러 loc 의 선두에 붙는 파라미터 소스 라벨(명세와 무관한 내부 라벨).
_PARAM_SOURCES = frozenset({"body", "query", "path", "header", "cookie", "form", "file"})

# 요청 본문을 JSON 으로 받는 미디어 타입(명세 §2.2). 그 외는 415.
_JSON_MEDIA_TYPE = "application/json"


def problem_type_uri(slug: str) -> str:
    """problem type 안정 URI 를 구성한다 (명세 §2.3 api M2 — 슬러그 불변)."""
    return f"{_PROBLEM_BASE}/{slug}"


def build_problem_body(
    *,
    slug: str,
    title: str,
    status: int,
    detail: Optional[str] = None,
    extra: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """RFC 9457 problem+json 바디를 만든다. extra 는 문서화된 확장 필드."""
    body: dict[str, Any] = {
        "type": problem_type_uri(slug),
        "title": title,
        "status": status,
    }
    if detail is not None:
        body["detail"] = detail
    if extra:
        body.update(extra)
    return body


def _problem_response(
    *,
    slug: str,
    title: str,
    status: int,
    detail: Optional[str] = None,
    extra: Optional[dict[str, Any]] = None,
) -> JsonResponse:
    body = build_problem_body(
        slug=slug, title=title, status=status, detail=detail, extra=extra
    )
    return JsonResponse(body, status=status, content_type=PROBLEM_CONTENT_TYPE)


def build_stock_contention_response(*, detail: Optional[str] = None) -> JsonResponse:
    """경합 소진 503 응답을 만든다(Retry-After 포함 — 명세 §2.3 api M4).

    일시적 경합 소진(StockContentionExhausted)이므로 409(out-of-stock, 영구)와
    type·의미를 분리하고, Retry-After 로 재시도 신호를 준다. 원자성(부분 변경 없음)은
    응용 서비스의 시도별 atomic 롤백이 보장한다(§3.3 — 표현 계층은 매핑만).
    """
    response = _problem_response(
        slug="stock-contention",
        title="Temporary contention, please retry.",
        status=503,
        detail=detail,
    )
    response["Retry-After"] = str(RETRY_AFTER_SECONDS)
    return response


def format_validation_errors(ninja_errors: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Ninja/Pydantic 검증 에러를 errors:[{field, reason}] 로 매핑 (명세 §2.3 api minor m2).

    loc 선두의 파라미터 소스 라벨(body 등)은 떼고, 남은 필드 경로를 '.' 로 잇는다.
    필드 경로가 없으면 소스 라벨을 field 로 둔다.
    """
    formatted: list[dict[str, str]] = []
    for error in ninja_errors:
        loc = tuple(error.get("loc", ()))
        path = loc[1:] if loc and loc[0] in _PARAM_SOURCES else loc
        if path:
            field = ".".join(str(part) for part in path)
        elif loc:
            field = str(loc[0])
        else:
            field = ""
        formatted.append({"field": field, "reason": str(error.get("msg", ""))})
    return formatted


def is_unsupported_media_type(request: HttpRequest) -> bool:
    """요청 Content-Type 이 JSON 이 아니면 415 대상이다 (명세 §2.3 api M1).

    malformed JSON(400)과 미지원 미디어 타입(415)을 요청 Content-Type 으로 가른다.
    """
    return request.content_type != _JSON_MEDIA_TYPE


def register_problem_handlers(api: NinjaAPI) -> None:
    """ordering API 의 에러 계약(409/404/422/415/400/503)을 problem+json 으로 등록한다."""

    @api.exception_handler(StockContentionExhausted)
    def _on_stock_contention(
        request: HttpRequest, exc: StockContentionExhausted
    ) -> JsonResponse:
        # 경합 재시도 소진(일시적). 503 + Retry-After 로 재시도 신호 — 409(영구
        # 재고 부족)와 의미 분리(명세 §2.3 api M4).
        return build_stock_contention_response(detail=str(exc))

    @api.exception_handler(OutOfStock)
    def _on_out_of_stock(request: HttpRequest, exc: OutOfStock) -> JsonResponse:
        # 재고 부족(영구 거절). requested 는 요청 수량 에코(명세 §2.3 409 확장).
        return _problem_response(
            slug="out-of-stock",
            title="Insufficient stock.",
            status=409,
            detail=str(exc),
            extra={"requested": exc.requested},
        )

    @api.exception_handler(ProductNotFound)
    def _on_product_not_found(request: HttpRequest, exc: ProductNotFound) -> JsonResponse:
        return _problem_response(
            slug="product-not-found",
            title="Product not found.",
            status=404,
            detail=str(exc),
        )

    @api.exception_handler(InvalidQuantity)
    def _on_invalid_quantity(request: HttpRequest, exc: InvalidQuantity) -> JsonResponse:
        # 도메인 백스톱 — 스키마 검증이 1차로 차단하지만 도메인이 최종 방어선.
        return _problem_response(
            slug="validation-error",
            title="Request validation failed.",
            status=422,
            detail=str(exc),
            extra={"errors": [{"field": "quantity", "reason": str(exc)}]},
        )

    @api.exception_handler(ValidationError)
    def _on_validation_error(request: HttpRequest, exc: ValidationError) -> JsonResponse:
        return _problem_response(
            slug="validation-error",
            title="Request validation failed.",
            status=422,
            extra={"errors": format_validation_errors(exc.errors)},
        )

    @api.exception_handler(HttpError)
    def _on_http_error(request: HttpRequest, exc: HttpError) -> JsonResponse:
        # Ninja 는 본문 파싱 실패를 HttpError(400)으로 올린다. 요청 Content-Type 이
        # JSON 이 아니면 415, malformed JSON 이면 400 으로 가른다(명세 §2.3 api M1).
        if exc.status_code == 400 and is_unsupported_media_type(request):
            return _problem_response(
                slug="unsupported-media-type",
                title="Unsupported media type.",
                status=415,
            )
        return _problem_response(
            slug="bad-request",
            title="Malformed request.",
            status=exc.status_code,
            detail=str(exc),
        )
