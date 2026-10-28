from __future__ import annotations

from typing import TYPE_CHECKING

from .count_stock_frame import CountStockFrame

if TYPE_CHECKING:
    from .count_memory import CountMemory


class ShelfCount:
    def __init__(self, frame: CountStockFrame) -> None:
        self._frame: CountStockFrame = frame

    def count(self, memory: CountMemory) -> None:
        self._frame.record_done(memory.shelf_id)
        memory.counted = True
