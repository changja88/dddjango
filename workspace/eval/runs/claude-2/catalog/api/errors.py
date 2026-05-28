"""표현 계층 에러 변환 — 도메인 예외·검증·미디어타입을 problem+json으로(설계 명세 section 2.6).

모든 에러 응답은 application/problem+json(RFC 9457)으로 통일한다.
instance는 요청별 식별자(req-<request_id>)를 붙인다(설계 명세 section 2.6 instance 정책).
"""

from __future__ import annotations

import uuid
from typing import Any

from django.http import HttpRequest, HttpResponse
from ninja import NinjaAPI
from ninja.errors import ValidationError

from catalog.domain.exceptions import InsufficientStockError, ProductNotFoundError

PROBLEM_CONTENT_TYPE = "application/problem+json"


class UnsupportedMediaTypeError(Exception):
    """요청 본문 Content-Type이 application/json이 아닐 때(설계 명세 section 2.5 -> 415).

    콘텐츠 협상은 표현 계층 관심사이므로 어댑터 파서가 발생시키고,
    여기 핸들러가 problem+json으로 변환한다(에러 포맷 단일 출처).
    """

TYPE_INSUFFICIENT_STOCK = "https://errors.example.com/catalog/insufficient-stock"
TYPE_PRODUCT_NOT_FOUND = "https://errors.example.com/catalog/product-not-found"
TYPE_VALIDATION_ERROR = "https://errors.example.com/catalog/validation-error"
TYPE_UNSUPPORTED_MEDIA_TYPE = (
    "https://errors.example.com/catalog/unsupported-media-type"
)


def _instance(request: HttpRequest) -> str:
    """요청별 식별 가능한 instance 경로를 만든다(설계 명세 section 2.6)."""
    return f"/api/v1/orders/req-{uuid.uuid4().hex}"


def _problem_response(
    api: NinjaAPI,
    request: HttpRequest,
    status: int,
    payload: dict[str, Any],
) -> HttpResponse:
    response = api.create_response(request, payload, status=status)
    response["Content-Type"] = PROBLEM_CONTENT_TYPE
    return response


def register_exception_handlers(api: NinjaAPI) -> None:
    """NinjaAPI 인스턴스에 problem+json 변환 핸들러를 등록한다."""

    @api.exception_handler(InsufficientStockError)
    def _on_insufficient_stock(
        request: HttpRequest, exc: InsufficientStockError
    ) -> HttpResponse:
        return _problem_response(
            api,
            request,
            409,
            {
                "type": TYPE_INSUFFICIENT_STOCK,
                "title": "Insufficient stock",
                "status": 409,
                "detail": (
                    f"Requested quantity {exc.requested} exceeds available "
                    f"stock {exc.available}."
                ),
                "instance": _instance(request),
                "product_id": exc.product_id,
                "requested": exc.requested,
                "available": exc.available,
            },
        )

    @api.exception_handler(ProductNotFoundError)
    def _on_product_not_found(
        request: HttpRequest, exc: ProductNotFoundError
    ) -> HttpResponse:
        return _problem_response(
            api,
            request,
            404,
            {
                "type": TYPE_PRODUCT_NOT_FOUND,
                "title": "Product not found",
                "status": 404,
                "detail": f"Product {exc.product_id} does not exist.",
                "instance": _instance(request),
                "product_id": exc.product_id,
            },
        )

    @api.exception_handler(UnsupportedMediaTypeError)
    def _on_unsupported_media_type(
        request: HttpRequest, exc: UnsupportedMediaTypeError
    ) -> HttpResponse:
        return _problem_response(
            api,
            request,
            415,
            {
                "type": TYPE_UNSUPPORTED_MEDIA_TYPE,
                "title": "Unsupported media type",
                "status": 415,
                "detail": "Request body must be application/json.",
                "instance": _instance(request),
            },
        )

    @api.exception_handler(ValidationError)
    def _on_validation_error(
        request: HttpRequest, exc: ValidationError
    ) -> HttpResponse:
        errors = [
            {
                "field": ".".join(str(part) for part in err.get("loc", [])),
                "message": err.get("msg", ""),
            }
            for err in exc.errors
        ]
        detail = errors[0]["message"] if errors else "Request validation failed."
        return _problem_response(
            api,
            request,
            422,
            {
                "type": TYPE_VALIDATION_ERROR,
                "title": "Request validation failed",
                "status": 422,
                "detail": detail,
                "instance": _instance(request),
                "errors": errors,
            },
        )
