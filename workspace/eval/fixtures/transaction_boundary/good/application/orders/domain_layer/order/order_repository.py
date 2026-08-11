from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from application.orders.domain_layer.order.order import Order


class OrderRepository(ABC):
    @abstractmethod
    def get(self, order_id: str) -> Order: ...

    @abstractmethod
    def list_open(self) -> Sequence[Order]: ...

    @abstractmethod
    def save(self, order: Order) -> None: ...

    @abstractmethod
    def remove(self, order: Order) -> None: ...
