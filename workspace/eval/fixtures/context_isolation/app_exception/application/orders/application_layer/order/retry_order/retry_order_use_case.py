from __future__ import annotations

from application.orders.application_layer.order.retry_order.retry_order_command import RetryOrderCommand
from application.orders.application_layer.order.retry_order.retry_order_result import RetryOrderResult


class _RetryOrder(RuntimeError):
    pass



class RetryOrderUseCase:
    def execute(self, command: RetryOrderCommand) -> RetryOrderResult:
        if not command.order_id:
            raise _RetryOrder("empty")
        return RetryOrderResult(order_id=command.order_id)
