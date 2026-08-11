from __future__ import annotations

from abc import ABC, abstractmethod

from application.orders.domain_layer.order.order import Order


class OrderRepository(ABC):
    @abstractmethod
    def get(self, order_id: str) -> Order: ...

    @abstractmethod
    def save(self, order: Order) -> None: ...
