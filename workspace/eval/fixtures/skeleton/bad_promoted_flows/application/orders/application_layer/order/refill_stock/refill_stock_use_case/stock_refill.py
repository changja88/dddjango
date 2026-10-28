from __future__ import annotations

from .refill_stock_frame import RefillStockFrame


class _StockRefill:
    def __init__(self, frame: RefillStockFrame) -> None:
        self._frame: RefillStockFrame = frame

    def run(self, sku_id: int) -> None:
        self._check(sku_id)
        self._frame._commit_refill(sku_id)

    def _check(self, sku_id: int) -> None:
        assert sku_id > 0
