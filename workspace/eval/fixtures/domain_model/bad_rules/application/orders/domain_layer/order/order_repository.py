from __future__ import annotations

from abc import ABC, abstractmethod


class OrderRepository(ABC):
    @abstractmethod
    def get(self, order_id: str) -> object: ...

    @abstractmethod
    def list_open(self) -> list: ...

    @abstractmethod
    def save(self, order: object) -> None: ...

    @abstractmethod
    def save_all(self, orders: list) -> None: ...
