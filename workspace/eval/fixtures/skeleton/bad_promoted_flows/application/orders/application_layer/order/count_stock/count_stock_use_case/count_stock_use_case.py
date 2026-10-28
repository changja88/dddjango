from __future__ import annotations

from typing import Callable

from application.orders.application_layer.order.count_stock.count_stock_command import CountStockCommand
from application.orders.application_layer.order.count_stock.count_stock_result import CountStockResult
from application.orders.application_layer.port.unit_of_work.order_unit_of_work import OrderUnitOfWork

from .count_memory import CountMemory
from .count_stock_frame import CountStockFrame
from .shelf_count import ShelfCount


class CountStockUseCase:
    def __init__(self, new_unit_of_work: Callable[[], OrderUnitOfWork]) -> None:
        self._frame: CountStockFrame = CountStockFrame(new_unit_of_work)
        self._shelf_count: ShelfCount = ShelfCount(frame=self._frame)

    def execute(self, command: CountStockCommand) -> CountStockResult:
        memory: CountMemory = CountMemory(shelf_id=command.target_id)
        self._shelf_count.count(memory)
        return CountStockResult(target_id=command.target_id, done=memory.counted)
