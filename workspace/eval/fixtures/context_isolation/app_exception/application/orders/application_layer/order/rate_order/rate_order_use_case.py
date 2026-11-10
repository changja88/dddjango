from __future__ import annotations

from application.orders.application_layer.order.rate_order.rate_order_command import RateOrderCommand
from application.orders.application_layer.order.rate_order.rate_order_result import RateOrderResult
from application.orders.application_layer.order.rate_order.exception import RateOrderRejected


class RateOrderUseCase:
    def execute(self, command: RateOrderCommand) -> RateOrderResult:
        if not command.order_id:
            raise RateOrderRejected("empty")
        return RateOrderResult(order_id=command.order_id)
