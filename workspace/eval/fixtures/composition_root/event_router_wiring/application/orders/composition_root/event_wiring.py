from application.orders.driving_layer.event_subscription import event_router
from framework.broker.internal.internal_broker import internal_broker


def wire_order_events() -> None:
    for event_type, handler in event_router.ROUTES.items():
        internal_broker.subscribe(event_type, handler)
