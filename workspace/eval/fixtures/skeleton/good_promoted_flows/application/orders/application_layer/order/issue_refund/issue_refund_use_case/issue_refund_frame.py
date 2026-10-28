from __future__ import annotations

from typing import Callable

from application.orders.application_layer.port.unit_of_work.order_unit_of_work import OrderUnitOfWork

from .refund_memory import _RefundMemory


class IssueRefundFrame:
    def __init__(self, new_unit_of_work: Callable[[], OrderUnitOfWork]) -> None:
        self._new_unit_of_work: Callable[[], OrderUnitOfWork] = new_unit_of_work

    def record_refund(self, memory: _RefundMemory) -> None:
        with self._new_unit_of_work() as unit_of_work:
            unit_of_work.mark_done(memory.refund_id)
        memory.sent = True
