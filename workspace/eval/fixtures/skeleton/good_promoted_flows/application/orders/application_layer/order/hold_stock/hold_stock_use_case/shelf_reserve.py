from __future__ import annotations

from .hold_stock_frame import HoldStockFrame
from .stock_memory import StockMemory


class ShelfReserve:
    def __init__(self, frame: HoldStockFrame) -> None:
        self._frame: HoldStockFrame = frame

    def reserve(self, sku_id: int) -> bool:
        memory: StockMemory = StockMemory(sku_id=sku_id)
        self._frame.record_hold(memory)
        return memory.held
