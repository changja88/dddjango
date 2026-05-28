"""Ninja 라우터 — POST /orders (얇은 표현 어댑터, 설계 명세 section 4, 5.3).

요청 파싱 -> create_order 호출 -> schema_out 응답. 도메인 예외/검증/미디어타입은
errors.py의 예외 핸들러가 problem+json으로 변환한다(어댑터에 분류 로직 없음).
"""

from __future__ import annotations

from http import HTTPStatus

from django.http import HttpRequest, HttpResponse
from ninja import NinjaAPI, Router
from ninja.errors import HttpError

from catalog.api.errors import UnsupportedMediaTypeError, register_exception_handlers
from catalog.api.parser import JsonOnlyParser
from catalog.api.schemas import CreateOrderIn, CreateOrderOut, ProblemDetail
from catalog.application.create_order import create_order
from catalog.application.dto import CreateOrderCommand
from catalog.repositories.order_repository import DjangoOrderRepository
from catalog.repositories.product_repository import DjangoProductRepository

router = Router(tags=["orders"])


@router.post(
    "/orders",
    response={
        201: CreateOrderOut,
        404: ProblemDetail,
        409: ProblemDetail,
        415: ProblemDetail,
        422: ProblemDetail,
    },
    summary="Create an order, deducting stock",
    description=(
        "재고가 충분하면 재고를 차감하며 주문을 생성하고 201을 반환한다. "
        "재고가 부족하면 409, 상품이 없으면 404로 거절한다(problem+json)."
    ),
)
def create_order_endpoint(
    request: HttpRequest, payload: CreateOrderIn
) -> tuple[int, CreateOrderOut]:
    result = create_order(
        CreateOrderCommand(
            product_id=payload.product_id, quantity=payload.quantity
        ),
        product_repository=DjangoProductRepository(),
        order_repository=DjangoOrderRepository(),
    )
    return HTTPStatus.CREATED, CreateOrderOut(
        order_id=result.order_id,
        product_id=result.product_id,
        quantity=result.quantity,
        status=result.status,
        remaining_stock=result.remaining_stock,
    )


class CatalogNinjaAPI(NinjaAPI):
    """본문 파싱 단계에서 감싸진 UnsupportedMediaTypeError를 415 핸들러로 되돌린다.

    Ninja의 BodyModel.get_request_data는 parse_body의 모든 예외를 HttpError(400)으로
    감싼다. JsonOnlyParser가 발생시킨 콘텐츠 협상 예외(__cause__)는 그 400이 아니라
    설계 명세 section 2.5의 415 problem+json으로 변환되어야 하므로 여기서 풀어 재디스패치한다.
    """

    def on_exception(self, request: HttpRequest, exc: Exception) -> HttpResponse:
        if isinstance(exc, HttpError) and isinstance(
            exc.__cause__, UnsupportedMediaTypeError
        ):
            return super().on_exception(request, exc.__cause__)
        return super().on_exception(request, exc)


def build_api() -> NinjaAPI:
    """NinjaAPI 인스턴스를 조립한다(라우터 등록 + 에러 핸들러)."""
    api = CatalogNinjaAPI(
        version="1.0.0", title="Catalog API", parser=JsonOnlyParser()
    )
    register_exception_handlers(api)
    api.add_router("", router)
    return api


api = build_api()
