from __future__ import annotations

from application.orders.application_layer.order.pack_order.pack_order_command import PackOrderCommand
from application.orders.application_layer.order.pack_order.pack_order_result import PackOrderResult
from application.orders.application_layer.order.pack_order.pack_order_use_case.pack_memory import _PackMiss


class PackOrderUseCase:
    def execute(self, command: PackOrderCommand) -> PackOrderResult:
        if not command.order_id:
            raise _PackMiss("empty")
        return PackOrderResult(order_id=command.order_id)
