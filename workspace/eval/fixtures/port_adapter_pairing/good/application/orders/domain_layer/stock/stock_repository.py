from __future__ import annotations

from abc import ABC, abstractmethod


class StockRepository(ABC):
    @abstractmethod
    def get(self, stock_id: str) -> object: ...

    @abstractmethod
    def save(self, stock: object) -> None: ...
