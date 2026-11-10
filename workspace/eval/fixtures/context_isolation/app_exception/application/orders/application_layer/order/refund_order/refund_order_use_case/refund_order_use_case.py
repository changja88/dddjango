from __future__ import annotations

from application.orders.application_layer.order.refund_order.refund_order_command import RefundOrderCommand
from application.orders.application_layer.order.refund_order.refund_order_result import RefundOrderResult
from .refund_order_failure import _RefundOrderFailure


class RefundOrderUseCase:
    def execute(self, command: RefundOrderCommand) -> RefundOrderResult:
        if not command.order_id:
            raise _RefundOrderFailure("empty")
        return RefundOrderResult(order_id=command.order_id)
