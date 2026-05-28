"""POST /orders 뷰 — 얇은 입력 어댑터(§5.2).

요청 파싱·검증 → 응용 유스케이스 호출 → 응답/예외를 HTTP로 변환한다.
입력 검증 실패는 도메인·DB 도달 전에 400으로 거절한다(필드 검증 errors 맵 / JSON 파싱 실패 detail만 — §2.5).
허용되지 않은 메서드는 405 + Allow: POST + Problem Details(§2.3).
"""
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from application.catalog.application_layer.place_order.command.place_order_app import (
    PlaceOrderApp,
)
from application.catalog.domain_layer.order.exception import ProductNotFound
from application.catalog.domain_layer.product.exception import InsufficientStock
from application.catalog.infra_layer.repository.django_order_repository import (
    DjangoOrderRepository,
)
from application.catalog.infra_layer.repository.django_product_repository import (
    DjangoProductRepository,
)
from application.catalog.presentation_layer.schema import error_out, schema_out
from application.catalog.presentation_layer.schema.schema_in import (
    JsonParseError,
    ValidationError,
    parse_place_order,
)

PROBLEM_JSON = "application/problem+json"


def _problem(body: dict, status: int) -> JsonResponse:
    return JsonResponse(body, status=status, content_type=PROBLEM_JSON)


@csrf_exempt
def place_order(request: HttpRequest) -> HttpResponse:
    if request.method != "POST":
        response = _problem(error_out.method_not_allowed(), status=405)
        response["Allow"] = "POST"
        return response

    try:
        command = parse_place_order(request.body)
    except JsonParseError as exc:
        return _problem(error_out.invalid_json(exc.detail), status=400)
    except ValidationError as exc:
        return _problem(error_out.invalid_request(exc.errors), status=400)

    app = PlaceOrderApp(
        product_repository=DjangoProductRepository(),
        order_repository=DjangoOrderRepository(),
    )

    try:
        result = app.execute(command)
    except ProductNotFound as exc:
        return _problem(error_out.product_not_found(exc.product_id), status=404)
    except InsufficientStock as exc:
        return _problem(
            error_out.insufficient_stock(
                product_id=command.product_id,
                available_stock=exc.available_stock,
                requested_quantity=exc.requested_quantity,
            ),
            status=409,
        )

    response = JsonResponse(
        schema_out.order_created_body(result),
        status=201,
        content_type="application/json",
    )
    response["Location"] = f"/orders/{result.id}"
    return response
