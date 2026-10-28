from __future__ import annotations

from typing import Callable

from application.orders.application_layer.order.issue_refund.issue_refund_command import IssueRefundCommand
from application.orders.application_layer.order.issue_refund.issue_refund_result import IssueRefundResult
from application.orders.application_layer.port.unit_of_work.order_unit_of_work import OrderUnitOfWork

from .card_refund import CardRefund
from .issue_refund_frame import IssueRefundFrame
from .refund_memory import _RefundMemory


class IssueRefundUseCase:
    def __init__(self, new_unit_of_work: Callable[[], OrderUnitOfWork]) -> None:
        self._frame: IssueRefundFrame = IssueRefundFrame(new_unit_of_work)
        self._card_refund: CardRefund = CardRefund(frame=self._frame)

    def execute(self, command: IssueRefundCommand) -> IssueRefundResult:
        memory: _RefundMemory = _RefundMemory(refund_id=command.target_id)
        self._card_refund.run(memory)
        return IssueRefundResult(target_id=command.target_id, done=memory.sent)
