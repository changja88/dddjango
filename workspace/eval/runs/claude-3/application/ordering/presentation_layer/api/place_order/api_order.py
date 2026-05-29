"""주문 생성 HTTP 어댑터 (명세 §2.2·§4.1).

얇은 어댑터: 요청 스키마 바인딩 → 응용 서비스 호출 → 201 응답·Location 헤더 매핑.
응용 서비스는 ACL·리포지토리를 조립해 주입한다(조립 책임은 표현 계층 진입점).

에러(409/404/422/415/400/503)는 중앙 exception_handler 가 problem+json 으로 변환한다
(ordering_api_router.register_problem_handlers). 여기서는 OpenAPI 에 드러내기 위해
response 스키마로 각 상태를 선언만 한다(명세 §4.5). 503(경합 소진)은 Retry-After
헤더를 함께 싣는다(명세 §2.3 api M4).
"""
from django.http import HttpRequest, HttpResponse
from ninja import Router

from application.ordering.application_layer.place_order.command.place_order_app import (
    PlaceOrderApp,
)
from application.ordering.application_layer.place_order.dto.place_order_command import (
    PlaceOrderCommand,
)
from application.ordering.infra_layer.acl.catalog_acl import DjangoProductStockPort
from application.ordering.infra_layer.repository.order_repository import (
    DjangoOrderRepository,
)
from application.ordering.presentation_layer.schema.error_out import (
    OutOfStockProblemOut,
    ProblemDetailOut,
    StockContentionProblemOut,
    ValidationProblemOut,
)
from application.ordering.presentation_layer.schema.schema_in import PlaceOrderIn
from application.ordering.presentation_layer.schema.schema_out import PlaceOrderOut

router = Router(tags=["orders"])


def _build_place_order_app() -> PlaceOrderApp:
    return PlaceOrderApp(
        stock_port=DjangoProductStockPort(),
        order_repository=DjangoOrderRepository(),
    )


@router.post(
    "/orders",
    response={
        201: PlaceOrderOut,
        400: ProblemDetailOut,
        404: ProblemDetailOut,
        409: OutOfStockProblemOut,
        415: ProblemDetailOut,
        422: ValidationProblemOut,
        503: StockContentionProblemOut,
    },
    summary="Place an order",
    description="재고가 충분하면 주문을 생성하고 재고를 차감한다(가격 스냅샷 박제).",
)
def place_order(
    request: HttpRequest,
    payload: PlaceOrderIn,
    response: HttpResponse,
) -> tuple[int, PlaceOrderOut]:
    app = _build_place_order_app()
    result = app.execute(
        PlaceOrderCommand(product_id=payload.product_id, quantity=payload.quantity)
    )

    response["Location"] = f"/api/orders/{result.order_id}"
    return 201, PlaceOrderOut(
        order_id=result.order_id,
        product_id=result.product_id,
        quantity=result.quantity,
        unit_price=result.unit_price,
        total_price=result.total_price,
        status=result.status,
        created_at=result.created_at,
    )
