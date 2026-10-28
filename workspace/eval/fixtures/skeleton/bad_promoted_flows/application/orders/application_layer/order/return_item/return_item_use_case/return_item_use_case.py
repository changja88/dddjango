from __future__ import annotations

from typing import Callable

from application.orders.application_layer.order.return_item.return_item_command import ReturnItemCommand
from application.orders.application_layer.order.return_item.return_item_result import ReturnItemResult
from application.orders.application_layer.port.unit_of_work.order_unit_of_work import OrderUnitOfWork

from .item_refund import ItemRefund
from .return_item_frame import ReturnItemFrame


class ReturnItemUseCase:
    def __init__(self, new_unit_of_work: Callable[[], OrderUnitOfWork]) -> None:
        self._frame: ReturnItemFrame = ReturnItemFrame(new_unit_of_work)
        self._item_refund: ItemRefund = ItemRefund(self._retry_refund)

    def _retry_refund(self, item_id: int) -> None:
        self._frame.record_done(item_id)

    def execute(self, command: ReturnItemCommand) -> ReturnItemResult:
        self._item_refund.refund(command.target_id)
        return ReturnItemResult(target_id=command.target_id, done=True)
