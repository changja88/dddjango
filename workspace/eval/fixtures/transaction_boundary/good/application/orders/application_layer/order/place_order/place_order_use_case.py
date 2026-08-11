from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order_repository import OrderRepository


class PlaceOrderUseCase:
    def __init__(self, repository: OrderRepository, unit_of_work: OrdersUnitOfWork) -> None:
        self._repository: OrderRepository = repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, order_id: str) -> None:
        with self._unit_of_work:
            order = self._repository.get(order_id)
            order.place("sku-1", 2)
            self._repository.save(order)
