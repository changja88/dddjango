from typing import Protocol

from application.catalog.domain_layer.order.order import Order


class OrderRepository(Protocol):
    def save(self, order: Order) -> int:
        ...

