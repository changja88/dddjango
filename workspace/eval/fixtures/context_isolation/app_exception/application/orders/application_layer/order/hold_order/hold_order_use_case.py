from __future__ import annotations

from application.orders.application_layer.order.hold_order.hold_order_command import HoldOrderCommand
from application.orders.application_layer.order.hold_order.hold_order_result import HoldOrderResult


class HoldOrderRejected(ValueError):
    pass



class HoldOrderUseCase:
    def execute(self, command: HoldOrderCommand) -> HoldOrderResult:
        if not command.order_id:
            raise HoldOrderRejected("empty")
        return HoldOrderResult(order_id=command.order_id)
