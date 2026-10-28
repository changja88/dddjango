from typing import Protocol

from application.orders.domain_layer.order.order import Order


class OrderRepository(Protocol):
    def find_by_id(self, order_id: int) -> Order: ...

    def save(self, order: Order) -> None: ...
