from __future__ import annotations

from collections.abc import Callable

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order_repository import OrderRepository

from .refund_memory import RefundMemory, load_refund_memory
from .refund_order_frame import RefundOrderFrame


class RefundOrderUseCase:
    def __init__(self, order_repository: OrderRepository, new_unit_of_work: Callable[[], OrdersUnitOfWork]) -> None:
        self._order_repository: OrderRepository = order_repository
        self._frame: RefundOrderFrame = RefundOrderFrame(order_repository, new_unit_of_work)

    def execute(self, order_id: str) -> bool:
        memory: RefundMemory = load_refund_memory(self._order_repository, order_id)
        if not memory.was_open:
            return False
        return self._frame.commit_order_change(order_id, lambda current: current.refund())
