from application.orders.event_subscription.event_router import route_order_events
from framework.broker.internal.internal_broker import internal_broker


def wire_order_events() -> None:
    internal_broker.subscribe(route_order_events)
