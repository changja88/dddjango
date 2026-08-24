from __future__ import annotations

from application.orders.domain_layer.stock.event.stock_adjusted import StockAdjusted


class Stock:
    def __init__(self, stock_id: str) -> None:
        self.stock_id: str = stock_id
        self._events: list = []

    def adjust(self, amount: int) -> None:
        self._amount: int = amount
        self._events.append(StockAdjusted())

    def pull_events(self) -> list:
        drained: list = list(self._events)
        self._events.clear()
        return drained
