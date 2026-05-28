import json
from json import JSONDecodeError
from typing import Any, Optional

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from application.catalog.application_layer.create_order.command.create_order_app import (
    CreateOrderApp,
)
from application.catalog.application_layer.create_order.dto.create_order_command import (
    CreateOrderCommand,
)
from application.catalog.application_layer.create_order.dto.create_order_result import (
    CreateOrderResult,
)
from application.catalog.domain_layer.product.exception import (
    DatabaseBusy,
    InsufficientStock,
    InvalidReserveQuantity,
    ProductNotFound,
)
from application.catalog.infra_layer.repository.order_repository import DjangoOrderRepository
from application.catalog.infra_layer.repository.product_repository import DjangoProductRepository
from application.catalog.presentation_layer.schema.error_out import ProblemDetails
from application.catalog.presentation_layer.schema.schema_in import CreateOrderRequest
from application.catalog.presentation_layer.schema.schema_out import CreateOrderResponse


@csrf_exempt
def api_orders(request: HttpRequest) -> HttpResponse:
    if request.method != "POST":
        return problem_response(
            ProblemDetails(
                type="/problems/method-not-allowed",
                title="Method not allowed",
                status=405,
                detail="Only POST is allowed.",
            ),
            status=405,
        )

    if request.content_type != "application/json":
        return problem_response(
            ProblemDetails(
                type="/problems/unsupported-media-type",
                title="Unsupported media type",
                status=415,
                detail="Content-Type must be application/json.",
            ),
            status=415,
        )

    request_body, invalid_fields = parse_request(request)
    if request_body is None:
        return invalid_request(invalid_fields)

    if request_body.quantity < 1:
        return problem_response(
            ProblemDetails(
                type="/problems/invalid-order-quantity",
                title="Invalid order quantity",
                status=422,
                detail="Quantity must be at least 1.",
            ),
            status=422,
        )

    app = CreateOrderApp(
        product_repository=DjangoProductRepository(),
        order_repository=DjangoOrderRepository(),
    )

    try:
        result = app.create(
            CreateOrderCommand(
                product_id=request_body.product_id,
                quantity=request_body.quantity,
            )
        )
    except InsufficientStock as exc:
        return problem_response(
            ProblemDetails(
                type="/problems/insufficient-stock",
                title="Insufficient stock",
                status=409,
                detail="Requested quantity exceeds available stock.",
                extensions={
                    "product_id": exc.product_id,
                    "requested_quantity": exc.requested_quantity,
                    "available_stock": exc.available_stock,
                },
            ),
            status=409,
        )
    except ProductNotFound as exc:
        return problem_response(
            ProblemDetails(
                type="/problems/product-not-found",
                title="Product not found",
                status=404,
                detail="Product was not found.",
                extensions={"product_id": exc.product_id},
            ),
            status=404,
        )
    except InvalidReserveQuantity:
        return problem_response(
            ProblemDetails(
                type="/problems/invalid-order-quantity",
                title="Invalid order quantity",
                status=422,
                detail="Quantity must be at least 1.",
            ),
            status=422,
        )
    except DatabaseBusy:
        return problem_response(
            ProblemDetails(
                type="/problems/database-busy",
                title="Database busy",
                status=503,
                detail="Database is temporarily busy.",
            ),
            status=503,
        )

    return success_response(result)


def parse_request(request: HttpRequest) -> tuple[Optional[CreateOrderRequest], list[str]]:
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (JSONDecodeError, UnicodeDecodeError):
        return None, []

    if not isinstance(payload, dict):
        return None, []

    invalid_fields = [
        field_name
        for field_name in ("product_id", "quantity")
        if field_name not in payload or not _is_int(payload[field_name])
    ]
    if invalid_fields:
        return None, invalid_fields

    return (
        CreateOrderRequest(
            product_id=payload["product_id"],
            quantity=payload["quantity"],
        ),
        [],
    )


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def invalid_request(invalid_fields: list[str]) -> JsonResponse:
    extensions = {"invalid_fields": invalid_fields} if invalid_fields else {}
    return problem_response(
        ProblemDetails(
            type="/problems/invalid-request",
            title="Invalid request",
            status=400,
            detail="Request body must include integer product_id and quantity fields.",
            extensions=extensions,
        ),
        status=400,
    )


def success_response(result: CreateOrderResult) -> JsonResponse:
    response_body = CreateOrderResponse(
        order_id=result.order_id,
        product_id=result.product_id,
        quantity=result.quantity,
        unit_price=result.unit_price,
        total_price=result.total_price,
        remaining_stock=result.remaining_stock,
    )
    return JsonResponse(response_body.to_dict(), status=201)


def problem_response(problem: ProblemDetails, *, status: int) -> JsonResponse:
    return JsonResponse(
        problem.to_dict(),
        status=status,
        content_type="application/problem+json",
    )
