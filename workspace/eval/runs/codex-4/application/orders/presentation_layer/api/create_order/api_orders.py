import json
from json import JSONDecodeError
from typing import Any, Union

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from application.orders.application_layer.create_order.command.create_order_app import (
    CreateOrderApp,
)
from application.orders.application_layer.create_order.dto.create_order_command import (
    CreateOrderCommand,
)
from application.orders.domain_layer.order.exception import (
    InsufficientStock,
    InvalidQuantity,
)
from application.orders.domain_layer.order.port.product_inventory_port import (
    InventoryConflict,
    ProductNotFound,
)
from application.orders.infra_layer.acl.catalog_acl import DjangoProductInventoryPort
from application.orders.infra_layer.repository.order_repository import (
    DjangoOrderRepository,
)
from application.orders.infra_layer.service.transaction_runner import (
    DjangoTransactionRunner,
)
from application.orders.presentation_layer.schema.error_out import problem_response
from application.orders.presentation_layer.schema.schema_out import order_created_body


@csrf_exempt
@require_POST
def create_order_api(request: HttpRequest) -> HttpResponse:
    if request.content_type != "application/json":
        return problem_response(
            status=415,
            type_="/problems/unsupported-media-type",
            title="Unsupported Media Type",
            detail="Request Content-Type must be application/json.",
        )

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (JSONDecodeError, UnicodeDecodeError):
        return _invalid_request_response(
            detail="Request body must be valid JSON.",
            errors={"body": ["invalid_json"]},
        )

    command = _build_command(payload)
    if isinstance(command, JsonResponse):
        return command

    app = CreateOrderApp(
        order_repository=DjangoOrderRepository(),
        product_inventory_port=DjangoProductInventoryPort(),
        transaction_runner=DjangoTransactionRunner(),
    )
    try:
        result = app.execute(command)
    except InvalidQuantity:
        return _invalid_request_response(
            detail="Quantity must be a positive integer.",
            errors={"quantity": ["must_be_positive"]},
        )
    except ProductNotFound:
        return problem_response(
            status=404,
            type_="/problems/product-not-found",
            title="Product not found",
            detail="The requested product does not exist.",
        )
    except InsufficientStock as exc:
        return problem_response(
            status=409,
            type_="/problems/insufficient-stock",
            title="Insufficient stock",
            detail="The requested quantity exceeds available stock.",
            available_stock=exc.available_stock,
            requested_quantity=exc.requested_quantity,
        )
    except InventoryConflict:
        return problem_response(
            status=409,
            type_="/problems/inventory-conflict",
            title="Inventory conflict",
            detail="Inventory changed while creating the order. Retry the request.",
        )

    return JsonResponse(order_created_body(result), status=201)


def _build_command(payload: Any) -> Union[CreateOrderCommand, JsonResponse]:
    if not isinstance(payload, dict):
        return _invalid_request_response(
            detail="Request body must be a JSON object.",
            errors={"body": ["invalid_object"]},
        )

    errors: dict[str, list[str]] = {}
    product_id = _positive_integer_field(payload, "product_id", errors)
    quantity = _positive_integer_field(payload, "quantity", errors)
    if errors:
        return _invalid_request_response(
            detail="Request fields are invalid.",
            errors=errors,
        )
    return CreateOrderCommand(product_id=product_id, quantity=quantity)


def _positive_integer_field(
    payload: dict[str, Any],
    field_name: str,
    errors: dict[str, list[str]],
) -> int:
    if field_name not in payload:
        errors[field_name] = ["required"]
        return 0

    value = payload[field_name]
    if type(value) is not int:
        errors[field_name] = ["invalid_integer"]
        return 0

    if value <= 0:
        errors[field_name] = ["must_be_positive"]
        return 0

    return value


def _invalid_request_response(
    *,
    detail: str,
    errors: dict[str, list[str]],
) -> JsonResponse:
    return problem_response(
        status=400,
        type_="/problems/invalid-order-request",
        title="Invalid order request",
        detail=detail,
        errors=errors,
    )
