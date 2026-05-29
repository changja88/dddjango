from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from application.catalog.application_layer.reserve_product_stock.command.reserve_product_stock_app import (
    ProductNotFound,
    ReserveProductStockApp,
    StockReservationConflict,
)
from application.catalog.application_layer.reserve_product_stock.dto.reserve_product_stock_command import (
    ReserveProductStockCommand,
)
from application.catalog.domain_layer.product.exception import InsufficientStock
from application.catalog.infra_layer.repository.product_repository import (
    DjangoProductRepository,
)
from application.catalog.presentation_layer.schema.error_out import problem_response
from application.catalog.presentation_layer.schema.schema_in import (
    ReservationRequestValidationError,
    parse_reserve_product_stock_request,
)
from application.catalog.presentation_layer.schema.schema_out import (
    reserve_product_stock_response,
)


@csrf_exempt
@require_POST
def reserve_product_stock(request: HttpRequest, product_id: int) -> JsonResponse:
    if request.content_type != "application/json":
        return problem_response(
            status=415,
            problem_type="/problems/catalog/unsupported-media-type",
            title="Unsupported media type",
            detail="Request body must use application/json.",
        )

    try:
        request_body = parse_reserve_product_stock_request(request.body)
        result = ReserveProductStockApp(
            repository=DjangoProductRepository(),
        ).reserve(
            ReserveProductStockCommand(
                product_id=product_id,
                quantity=request_body.quantity,
            )
        )
    except ReservationRequestValidationError as exc:
        return problem_response(
            status=422,
            problem_type="/problems/catalog/invalid-reservation-request",
            title="Invalid reservation request",
            detail=exc.detail,
            extensions={"errors": exc.errors},
        )
    except ProductNotFound as exc:
        return problem_response(
            status=404,
            problem_type="/problems/catalog/product-not-found",
            title="Product not found",
            detail=f"Product {exc.product_id} was not found.",
        )
    except InsufficientStock as exc:
        return problem_response(
            status=409,
            problem_type="/problems/catalog/insufficient-stock",
            title="Insufficient stock",
            detail="Requested quantity exceeds available stock.",
            extensions={
                "requested_quantity": exc.requested_quantity,
                "available_stock": exc.available_stock,
            },
        )
    except StockReservationConflict:
        return problem_response(
            status=409,
            problem_type="/problems/catalog/stock-reservation-conflict",
            title="Stock reservation conflict",
            detail="Stock changed during reservation. Retry the request.",
        )

    return JsonResponse(reserve_product_stock_response(result), status=200)
