from __future__ import annotations

from application.orders.application_layer.order.cancel_order.cancel_order_command import CancelOrderCommand
from application.orders.application_layer.order.cancel_order.cancel_order_result import CancelOrderResult
from .cancel_order_failure import _CancelOrderFailure


class CancelOrderUseCase:
    def execute(self, command: CancelOrderCommand) -> CancelOrderResult:
        if not command.order_id:
            raise _CancelOrderFailure("empty")
        return CancelOrderResult(order_id=command.order_id)
