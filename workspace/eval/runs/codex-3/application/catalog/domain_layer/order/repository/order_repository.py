from typing import Protocol

from application.catalog.domain_layer.order.entity.order import Order


class OrderRepository(Protocol):
    def add(self, order: Order) -> Order:
        ...
