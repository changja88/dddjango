from __future__ import annotations

from typing import Callable

from application.orders.application_layer.order.hold_stock.hold_stock_command import HoldStockCommand
from application.orders.application_layer.order.hold_stock.hold_stock_result import HoldStockResult
from application.orders.application_layer.port.unit_of_work.order_unit_of_work import OrderUnitOfWork

from .hold_stock_frame import HoldStockFrame
from .shelf_reserve import ShelfReserve


class HoldStockUseCase:
    def __init__(self, new_unit_of_work: Callable[[], OrderUnitOfWork]) -> None:
        self._frame: HoldStockFrame = HoldStockFrame(new_unit_of_work)
        self._shelf_reserve: ShelfReserve = ShelfReserve(frame=self._frame)

    def execute(self, command: HoldStockCommand) -> HoldStockResult:
        return HoldStockResult(target_id=command.target_id, done=self._shelf_reserve.reserve(command.target_id))
