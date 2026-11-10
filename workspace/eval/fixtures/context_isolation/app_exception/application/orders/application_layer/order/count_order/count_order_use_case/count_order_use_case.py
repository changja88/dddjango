from __future__ import annotations

from application.orders.application_layer.order.count_order.count_order_command import CountOrderCommand
from application.orders.application_layer.order.count_order.count_order_result import CountOrderResult
from .count_order_failure import _CountOrderFailure


class CountOrderUseCase:
    def execute(self, command: CountOrderCommand) -> CountOrderResult:
        if not command.order_id:
            raise _CountOrderFailure("empty")
        return CountOrderResult(order_id=command.order_id)
