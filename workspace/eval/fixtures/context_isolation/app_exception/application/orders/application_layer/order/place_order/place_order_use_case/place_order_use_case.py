from __future__ import annotations

from application.orders.application_layer.order.place_order.place_order_command import PlaceOrderCommand
from application.orders.application_layer.order.place_order.place_order_result import PlaceOrderResult
from .place_order_failure import PlaceOrderFailure


class PlaceOrderUseCase:
    def execute(self, command: PlaceOrderCommand) -> PlaceOrderResult:
        if not command.order_id:
            raise PlaceOrderFailure("empty")
        return PlaceOrderResult(order_id=command.order_id)
