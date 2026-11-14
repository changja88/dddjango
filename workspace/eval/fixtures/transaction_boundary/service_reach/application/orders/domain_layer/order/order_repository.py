from __future__ import annotations

from abc import ABC, abstractmethod

from application.orders.domain_layer.order.order import Order


class OrderRepository(ABC):
    @abstractmethod
    def find(self, order_id: int) -> Order: ...

    @abstractmethod
    def find_for_update(self, order_id: int) -> Order: ...

    @abstractmethod
    def save_link(self, order: Order) -> None: ...
