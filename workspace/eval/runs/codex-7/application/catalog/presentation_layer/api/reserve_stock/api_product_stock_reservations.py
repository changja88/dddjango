import json
from json import JSONDecodeError
from typing import Any, Dict, List, Optional

from django.db import transaction
from django.http import HttpRequest, JsonResponse
from ninja import Router

from application.catalog.application_layer.reserve_stock.command.reserve_product_stock_app import (
    ProductNotFound,
    ReserveProductStockApp,
    StockReservationConflict,
)
from application.catalog.application_layer.reserve_stock.dto.reserve_product_stock_command import (
    ReserveProductStockCommand,
)
from application.catalog.domain_layer.product.exception import (
    InsufficientStock,
    InvalidReservationQuantity,
)
from application.catalog.infra_layer.repository.product_repository import (
    DjangoProductRepository,
)
from application.catalog.presentation_layer.schema.reserve_stock.error_out import (
    ProblemDetailsOut,
)
from application.catalog.presentation_layer.schema.reserve_stock.schema_in import (
    RESERVE_STOCK_REQUEST_BODY_OPENAPI,
)
from application.catalog.presentation_layer.schema.reserve_stock.schema_out import (
    ReserveStockOut,
)

router = Router(tags=["catalog"])


@router.post(
    "/products/{product_id}/stock-reservations",
    response={
        200: ReserveStockOut,
        400: ProblemDetailsOut,
        404: ProblemDetailsOut,
        409: ProblemDetailsOut,
        415: ProblemDetailsOut,
    },
    summary="Reserve product stock",
    openapi_extra=RESERVE_STOCK_REQUEST_BODY_OPENAPI,
)
def reserve_product_stock(request: HttpRequest, product_id: int) -> JsonResponse:
    unsupported_media_response = _reject_unsupported_media_type(request, product_id)
    if unsupported_media_response is not None:
        return unsupported_media_response

    try:
        quantity = _extract_quantity(request, product_id)
    except InvalidReservationRequest as error:
        return _invalid_request_response(
            product_id=product_id,
            errors=error.errors,
            detail=error.detail,
        )

    app = ReserveProductStockApp(
        repository=DjangoProductRepository(),
        transaction_context=transaction.atomic,
    )
    try:
        result = app.reserve(
            ReserveProductStockCommand(product_id=product_id, quantity=quantity)
        )
    except ProductNotFound:
        return _problem_response(
            status=404,
            body={
                "type": "/problems/product-not-found",
                "title": "Product not found",
                "status": 404,
                "detail": f"Product {product_id} was not found.",
                "instance": _reservation_path(product_id),
                "product_id": product_id,
            },
        )
    except InsufficientStock as error:
        return _problem_response(
            status=409,
            body={
                "type": "/problems/insufficient-product-stock",
                "title": "Insufficient product stock",
                "status": 409,
                "detail": (
                    f"Product {product_id} has insufficient stock for the requested "
                    "quantity."
                ),
                "instance": _reservation_path(product_id),
                "product_id": product_id,
                "requested_quantity": error.requested_quantity,
                "available_stock": error.available_stock,
            },
        )
    except StockReservationConflict:
        return _problem_response(
            status=409,
            body={
                "type": "/problems/product-stock-reservation-conflict",
                "title": "Product stock reservation conflict",
                "status": 409,
                "detail": (
                    "The stock reservation could not be completed because the product "
                    "was modified concurrently."
                ),
                "instance": _reservation_path(product_id),
                "product_id": product_id,
                "retryable": True,
            },
        )
    except InvalidReservationQuantity as error:
        return _invalid_request_response(
            product_id=product_id,
            errors=[
                {
                    "field": "quantity",
                    "message": str(error),
                    "code": "invalid_quantity",
                }
            ],
            detail="Reservation quantity must be a positive integer.",
        )

    response = JsonResponse({"product_id": result.product_id, "stock": result.stock})
    response["Cache-Control"] = "no-store"
    return response


class InvalidReservationRequest(Exception):
    def __init__(self, detail: str, errors: List[Dict[str, str]]) -> None:
        self.detail = detail
        self.errors = errors
        super().__init__(detail)


def _reject_unsupported_media_type(
    request: HttpRequest, product_id: int
) -> Optional[JsonResponse]:
    if not request.body:
        return None

    content_type = request.META.get("CONTENT_TYPE", "").split(";", 1)[0].lower()
    if content_type == "application/json":
        return None

    return _problem_response(
        status=415,
        body={
            "type": "/problems/unsupported-media-type",
            "title": "Unsupported media type",
            "status": 415,
            "detail": "Content-Type must be application/json.",
            "instance": _reservation_path(product_id),
        },
    )


def _extract_quantity(request: HttpRequest, product_id: int) -> int:
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except (JSONDecodeError, UnicodeDecodeError) as error:
        raise InvalidReservationRequest(
            detail="Request body must be valid JSON.",
            errors=[
                {
                    "field": "body",
                    "message": "Request body must be valid JSON.",
                    "code": "invalid_json",
                }
            ],
        ) from error

    if not isinstance(payload, dict):
        raise InvalidReservationRequest(
            detail="Request body must be a JSON object.",
            errors=[
                {
                    "field": "body",
                    "message": "Request body must be a JSON object.",
                    "code": "invalid_body",
                }
            ],
        )

    quantity = payload.get("quantity")
    if type(quantity) is not int:
        raise InvalidReservationRequest(
            detail="Reservation quantity is required and must be an integer.",
            errors=[
                {
                    "field": "quantity",
                    "message": "Reservation quantity is required and must be an integer.",
                    "code": "invalid_quantity",
                }
            ],
        )

    if quantity < 1:
        raise InvalidReservationRequest(
            detail="Reservation quantity must be a positive integer.",
            errors=[
                {
                    "field": "quantity",
                    "message": "Reservation quantity must be a positive integer.",
                    "code": "invalid_quantity",
                }
            ],
        )

    return quantity


def _invalid_request_response(
    product_id: int, errors: List[Dict[str, str]], detail: str
) -> JsonResponse:
    return _problem_response(
        status=400,
        body={
            "type": "/problems/invalid-reservation-request",
            "title": "Invalid reservation request",
            "status": 400,
            "detail": detail,
            "instance": _reservation_path(product_id),
            "errors": errors,
        },
    )


def _problem_response(status: int, body: Dict[str, Any]) -> JsonResponse:
    return JsonResponse(
        body,
        status=status,
        content_type="application/problem+json",
    )


def _reservation_path(product_id: int) -> str:
    return f"/api/catalog/products/{product_id}/stock-reservations"
