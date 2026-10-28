from __future__ import annotations

from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository


class SettleOrderFrame:
    def __init__(self, order_repository: OrderRepository) -> None:
        self._order_repository: OrderRepository = order_repository

    def find_order(self, order_id: str) -> Order:
        return self._order_repository.get(order_id)

    def save_order(self, order: Order) -> None:
        self._order_repository.save(order)
