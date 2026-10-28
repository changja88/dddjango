from __future__ import annotations

from typing import Callable

from application.orders.application_layer.order.split_bill.split_bill_command import SplitBillCommand
from application.orders.application_layer.order.split_bill.split_bill_result import SplitBillResult
from application.orders.application_layer.port.unit_of_work.order_unit_of_work import OrderUnitOfWork

from .bill_share import BillShare
from .split_bill_frame import SplitBillFrame


class SplitBillUseCase:
    def __init__(self, new_unit_of_work: Callable[[], OrderUnitOfWork]) -> None:
        self._frame: SplitBillFrame = SplitBillFrame(new_unit_of_work)
        self._bill_share: BillShare = BillShare(owner=self, frame=self._frame)

    def recount_bill(self, bill_id: int) -> None:
        self._frame.record_done(bill_id)

    def execute(self, command: SplitBillCommand) -> SplitBillResult:
        self._bill_share.share(command.target_id)
        return SplitBillResult(target_id=command.target_id, done=True)
