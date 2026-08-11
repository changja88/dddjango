from __future__ import annotations

from application.orders.domain_layer.order.order_repository import OrderRepository


class OrderController:
    def get_order(self, order_id: str) -> object:
        repository = OrderRepository()
        return repository
