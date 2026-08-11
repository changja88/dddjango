from __future__ import annotations

from abc import ABC, abstractmethod

from application.orders.domain_layer.order.order import Order


class OrderRepository(ABC):
    @abstractmethod
    def get(self, order_id: str) -> Order: ...

    def list_rows(self) -> "QuerySet[Order]":  # noqa: F821
        return None

    @abstractmethod
    def exists_open(self) -> bool: ...

    @abstractmethod
    def save(self, order: Order) -> None: ...

    @abstractmethod
    def add(self, order: Order) -> None: ...

    @abstractmethod
    def add_all(self, orders: object) -> None: ...

    @abstractmethod
    def update_status(self, order_id: str, status: str) -> None: ...

    @abstractmethod
    def save_note(self, note: str) -> None: ...
