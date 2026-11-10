from __future__ import annotations

from abc import ABC, abstractmethod

from application.orders.domain_layer.order.order import Order


class OrderRepository(ABC):
    @abstractmethod
    def get(self, order_id: str) -> Order: ...

    @abstractmethod
    def get_for_update(self, order_id: str) -> Order | None: ...

    @abstractmethod
    def find_by_customer(self, customer_id: str) -> list[Order]: ...

    @abstractmethod
    def save(self, order: Order) -> None: ...

    @abstractmethod
    def save_label(self, order: Order) -> None: ...

    @abstractmethod
    def save_with_version_guard(self, order: Order) -> bool: ...

    @abstractmethod
    def save_all(self, orders: list[Order]) -> None: ...

    @abstractmethod
    def remove(self, order: Order) -> None: ...

    @abstractmethod
    def remove_many(self, orders: tuple[Order, ...]) -> int: ...
