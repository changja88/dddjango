from __future__ import annotations

from django.db import transaction

from application.orders.domain_layer.order.order_repository import OrderRepository


class PlaceOrderUseCase:
    def __init__(self, repository: OrderRepository, unit_of_work: "OrdersUnitOfWork") -> None:  # noqa: F821
        self._repository: OrderRepository = repository
        self._unit_of_work: "OrdersUnitOfWork" = unit_of_work

    def execute(self, order_id: str) -> None:
        with self._unit_of_work:
            order = self._repository.get(order_id)
            order.status = "placed"
            self._repository.save(order)
            transaction.on_commit(self._notify)

    def _notify(self) -> None:
        return None
