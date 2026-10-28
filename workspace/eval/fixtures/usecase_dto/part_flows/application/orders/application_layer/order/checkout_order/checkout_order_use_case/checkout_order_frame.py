"""틀 부품 — 저장소를 쥐고 이름 있는 메서드로 읽고 쓴다."""
from __future__ import annotations

from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository


class CheckoutOrderFrame:
    def __init__(self, order_repository: OrderRepository) -> None:
        self._order_repository: OrderRepository = order_repository

    def load_order(self, order_id: str) -> Order:
        return self._order_repository.get(order_id)

    def commit_order(self, order: Order) -> None:
        self._order_repository.save(order)
