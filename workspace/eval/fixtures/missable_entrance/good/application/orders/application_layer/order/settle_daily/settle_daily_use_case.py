from __future__ import annotations

from application.orders.domain_layer.order.order_repository import OrderRepository


class SettleDailyUseCase:
    def __init__(self, repository: OrderRepository) -> None:
        self._repository: OrderRepository = repository

    def execute(self) -> None:
        for order in self._repository.list_open():
            order.settle()
            self._repository.save(order)
