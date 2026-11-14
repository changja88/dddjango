from application.orders.driving_layer.open_host_service.order_lookup.order_lookup_service import get_order_query
from application.orders.driving_layer.open_host_service.order_lookup.contract.request.get_order_request import GetOrderRequest
from application.orders.driving_layer.open_host_service.order_lookup.contract.exception.order_lookup_published_error import OrderLookupPublishedError
from application.orders.driving_layer import open_host_service
from pydantic import BaseModel


class SuspensionRow(BaseModel):
    order_id: str


def grant(order_id: str) -> str:
    try:
        return get_order_query(GetOrderRequest(order_id=order_id)).code
    except OrderLookupPublishedError:
        return "unavailable"


def next_page(page: object) -> object:
    return page.cursor()  # 창구가 준 페이지 값의 다음 쪽 — 날 SQL 이 아니다


WINDOW: object = open_host_service
