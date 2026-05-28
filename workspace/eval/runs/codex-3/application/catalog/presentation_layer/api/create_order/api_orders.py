import json
import time
from json import JSONDecodeError
from typing import Any, Dict, Optional

from django.db import OperationalError
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from application.catalog.application_layer.create_order.command.create_order_app import (
    CreateOrderApp,
)
from application.catalog.application_layer.create_order.dto.create_order_command import (
    CreateOrderCommand,
)
from application.catalog.domain_layer.order.entity.order import Order
from application.catalog.domain_layer.product.exception import (
    InsufficientStock,
    ProductNotFound,
)
from application.catalog.infra_layer.repository.catalog_unit_of_work import (
    DjangoCatalogUnitOfWork,
)
from application.catalog.presentation_layer.schema.schema_in import (
    InvalidOrderRequest,
    parse_create_order_command,
)
from application.catalog.presentation_layer.schema.schema_out import (
    order_to_response,
)


@csrf_exempt
@require_POST
def create_order(request: HttpRequest) -> HttpResponse:
    if _media_type(request.content_type) != "application/json":
        return problem_response(
            status=415,
            problem_type="urn:problem:catalog:unsupported-media-type",
            title="Unsupported media type",
            detail="Request content type must be application/json.",
        )

    try:
        payload = json.loads(request.body.decode("utf-8"))
        command = parse_create_order_command(payload)
        order = _create_order_with_sqlite_lock_retry(command)
    except (JSONDecodeError, UnicodeDecodeError):
        return problem_response(
            status=400,
            problem_type="urn:problem:catalog:invalid-order-request",
            title="Invalid order request",
            detail="Request body is invalid.",
            errors={"non_field_errors": ["Request body must be valid JSON."]},
        )
    except InvalidOrderRequest as error:
        return problem_response(
            status=400,
            problem_type="urn:problem:catalog:invalid-order-request",
            title="Invalid order request",
            detail="Request body is invalid.",
            errors=error.errors,
        )
    except ProductNotFound:
        return problem_response(
            status=404,
            problem_type="urn:problem:catalog:product-not-found",
            title="Product not found",
            detail="Product does not exist.",
        )
    except InsufficientStock:
        return problem_response(
            status=409,
            problem_type="urn:problem:catalog:insufficient-stock",
            title="Insufficient stock",
            detail="Request cannot be accepted because available stock is lower than requested quantity.",
        )

    return JsonResponse(order_to_response(order), status=201)


def _create_order_with_sqlite_lock_retry(command: CreateOrderCommand) -> Order:
    attempts = 4
    for attempt in range(attempts):
        try:
            return CreateOrderApp(DjangoCatalogUnitOfWork()).create(command)
        except OperationalError as error:
            if "locked" not in str(error).lower() or attempt == attempts - 1:
                raise
            time.sleep(0.02)
    raise RuntimeError("unreachable retry state")


def problem_response(
    *,
    status: int,
    problem_type: str,
    title: str,
    detail: str,
    errors: Optional[Dict[str, Any]] = None,
) -> JsonResponse:
    body: Dict[str, Any] = {
        "type": problem_type,
        "title": title,
        "status": status,
        "detail": detail,
    }
    if errors is not None:
        body["errors"] = errors
    return JsonResponse(body, status=status, content_type="application/problem+json")


def _media_type(content_type: str) -> str:
    return content_type.split(";", 1)[0].strip().lower()
