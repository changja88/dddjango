from application.orders.application_layer.order.place_order.place_order_use_case import PlaceOrderUseCase
from application.orders.event_subscription.event_router import route_order_events
from framework.broker.internal.internal_broker import internal_broker


def build_place_order_use_case() -> PlaceOrderUseCase:
    return PlaceOrderUseCase()


def wire_order_events() -> None:
    internal_broker.subscribe(route_order_events)
