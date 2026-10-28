from __future__ import annotations

from typing import Callable

from application.orders.application_layer.order.refill_stock.refill_stock_command import RefillStockCommand
from application.orders.application_layer.order.refill_stock.refill_stock_result import RefillStockResult
from application.orders.application_layer.port.unit_of_work.order_unit_of_work import OrderUnitOfWork

from .refill_stock_frame import RefillStockFrame
from .stock_refill import _StockRefill


class RefillStockUseCase:
    def __init__(self, new_unit_of_work: Callable[[], OrderUnitOfWork]) -> None:
        self._frame: RefillStockFrame = RefillStockFrame(new_unit_of_work)
        self._stock_refill: _StockRefill = _StockRefill(frame=self._frame)

    def execute(self, command: RefillStockCommand) -> RefillStockResult:
        self._stock_refill.run(command.target_id)
        return RefillStockResult(target_id=command.target_id, done=True)
