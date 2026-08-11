from __future__ import annotations

from application.orders.domain_layer.order.order_repository import OrderRepository
from application.orders.domain_layer.order.value_object.money import Money


class PlaceOrderUseCase:
    def __init__(self, repository: OrderRepository) -> None:
        self._repository: OrderRepository = repository

    def execute(self, order_id: str, amount: int) -> None:
        order = self._repository.get(order_id)
        order.place(Money(amount))
        self._repository.save(order)
