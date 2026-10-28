from __future__ import annotations

from abc import ABC, abstractmethod

from application.orders.domain_layer.stock.stock import Stock


class StockRepository(ABC):
    @abstractmethod
    def get(self, sku: str) -> Stock: ...

    @abstractmethod
    def save(self, stock: Stock) -> None: ...
