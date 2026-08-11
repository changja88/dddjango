from __future__ import annotations

from application.orders.domain_layer.order.order_repository import OrderRepository


class RecordPaymentUseCase:
    def __init__(self, repository: OrderRepository) -> None:
        self._repository: OrderRepository = repository

    def execute(self, payload: str) -> None:
        self._repository.save(payload)
