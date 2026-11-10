from __future__ import annotations

from application.orders.application_layer.order.ship_order.ship_order_use_case import ship_order_failure
from application.orders.application_layer.order.ship_order.ship_order_use_case import ShipOrderUseCase
from application.orders.application_layer.order.ship_order.ship_order_command import ShipOrderCommand


def ship_order(order_id: str) -> str:
    try:
        ShipOrderUseCase().execute(ShipOrderCommand(order_id=order_id))
    except ship_order_failure._ShipOrderFailure as failure:
        return failure.category
    return order_id
