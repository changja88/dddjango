from __future__ import annotations

from application.orders.domain_layer.order.order_repository import OrderRepository


class RecordPaymentUseCase:
    def __init__(self, repository: OrderRepository) -> None:
        self._repository: OrderRepository = repository

    def execute(self, payload: str) -> str:
        order = self._repository.get(payload)
        order.settle()
        self._repository.save(order)
        return "done"
