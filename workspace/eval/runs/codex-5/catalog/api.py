from __future__ import annotations

import json
from json import JSONDecodeError
from typing import Any

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from catalog.models import InsufficientStock, InvalidReservationQuantity
from catalog.repositories import ProductNotFound, StockReservationConflict
from catalog.services import ReservationResult, reserve_product_stock


PROBLEM_TYPES = {
    "product_not_found": "https://example.com/problems/product-not-found",
    "insufficient_stock": "https://example.com/problems/insufficient-stock",
    "stock_reservation_conflict": "https://example.com/problems/stock-reservation-conflict",
    "validation_error": "https://example.com/problems/validation-error",
    "unsupported_media_type": "https://example.com/problems/unsupported-media-type",
    "not_acceptable": "https://example.com/problems/not-acceptable",
}


@csrf_exempt
def reserve_product(request: HttpRequest, product_id: int) -> HttpResponse:
    if not _accepts_json_response(request):
        return _problem_response(
            request,
            status=406,
            problem_type=PROBLEM_TYPES["not_acceptable"],
            title="Not acceptable",
            detail="The requested response representation is not available.",
        )

    if request.body and request.content_type != "application/json":
        return _problem_response(
            request,
            status=415,
            problem_type=PROBLEM_TYPES["unsupported_media_type"],
            title="Unsupported media type",
            detail="Request content type must be application/json.",
        )

    payload, invalid_params = _parse_payload(request)
    if invalid_params:
        return _validation_error_response(request, invalid_params)

    quantity, invalid_params = _parse_quantity(payload)
    if invalid_params:
        return _validation_error_response(request, invalid_params)

    try:
        result = reserve_product_stock(product_id, quantity)
    except ProductNotFound:
        return _problem_response(
            request,
            status=404,
            problem_type=PROBLEM_TYPES["product_not_found"],
            title="Product not found",
            detail="The requested product does not exist.",
        )
    except InsufficientStock:
        return _problem_response(
            request,
            status=409,
            problem_type=PROBLEM_TYPES["insufficient_stock"],
            title="Insufficient stock",
            detail="Product stock is lower than the requested quantity.",
        )
    except (InvalidReservationQuantity, StockReservationConflict):
        return _problem_response(
            request,
            status=409,
            problem_type=PROBLEM_TYPES["stock_reservation_conflict"],
            title="Stock reservation conflict",
            detail="The reservation could not be completed due to concurrent updates.",
        )

    return _success_response(result)


def _parse_payload(request: HttpRequest) -> tuple[dict[str, Any] | None, list[dict[str, str]]]:
    if not request.body:
        return None, [{"name": "body", "reason": "Request body is required."}]

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (UnicodeDecodeError, JSONDecodeError):
        return None, [{"name": "body", "reason": "Request body must be valid JSON."}]

    if not isinstance(payload, dict):
        return None, [{"name": "body", "reason": "Request body must be a JSON object."}]

    return payload, []


def _parse_quantity(payload: dict[str, Any] | None) -> tuple[int, list[dict[str, str]]]:
    if payload is None or "quantity" not in payload:
        return 0, [{"name": "quantity", "reason": "This field is required."}]

    quantity = payload["quantity"]
    if isinstance(quantity, bool) or not isinstance(quantity, int):
        return 0, [{"name": "quantity", "reason": "Input should be an integer."}]

    if quantity <= 0:
        return 0, [{"name": "quantity", "reason": "Input should be a positive integer."}]

    return quantity, []


def _accepts_json_response(request: HttpRequest) -> bool:
    accept_header = request.headers.get("Accept", "")
    if not accept_header:
        return True

    for item in accept_header.split(","):
        media_type, quality = _parse_accept_item(item)
        if quality > 0 and media_type in {
            "*/*",
            "application/*",
            "application/json",
            "application/problem+json",
        }:
            return True
    return False


def _parse_accept_item(item: str) -> tuple[str, float]:
    parts = [part.strip() for part in item.split(";") if part.strip()]
    if not parts:
        return "", 0

    quality = 1.0
    for parameter in parts[1:]:
        name, separator, value = parameter.partition("=")
        if separator and name.strip().lower() == "q":
            try:
                quality = float(value)
            except ValueError:
                quality = 0
            break

    return parts[0].lower(), quality


def _success_response(result: ReservationResult) -> JsonResponse:
    return JsonResponse(
        {
            "product_id": result.product_id,
            "reserved_quantity": result.reserved_quantity,
            "remaining_stock": result.remaining_stock,
        }
    )


def _validation_error_response(
    request: HttpRequest,
    invalid_params: list[dict[str, str]],
) -> JsonResponse:
    return _problem_response(
        request,
        status=422,
        problem_type=PROBLEM_TYPES["validation_error"],
        title="Validation error",
        detail="Request validation failed.",
        invalid_params=invalid_params,
    )


def _problem_response(
    request: HttpRequest,
    *,
    status: int,
    problem_type: str,
    title: str,
    detail: str,
    invalid_params: list[dict[str, str]] | None = None,
) -> JsonResponse:
    body: dict[str, Any] = {
        "type": problem_type,
        "title": title,
        "status": status,
        "detail": detail,
        "instance": request.path,
    }
    if invalid_params is not None:
        body["invalid_params"] = invalid_params

    return JsonResponse(body, status=status, content_type="application/problem+json")
