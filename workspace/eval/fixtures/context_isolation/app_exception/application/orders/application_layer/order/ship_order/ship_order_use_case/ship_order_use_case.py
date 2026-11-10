from __future__ import annotations

from application.orders.application_layer.order.ship_order.ship_order_command import ShipOrderCommand
from application.orders.application_layer.order.ship_order.ship_order_result import ShipOrderResult
from .ship_order_failure import _ShipOrderFailure


class ShipOrderUseCase:
    def execute(self, command: ShipOrderCommand) -> ShipOrderResult:
        if not command.order_id:
            raise _ShipOrderFailure("empty")
        return ShipOrderResult(order_id=command.order_id)
