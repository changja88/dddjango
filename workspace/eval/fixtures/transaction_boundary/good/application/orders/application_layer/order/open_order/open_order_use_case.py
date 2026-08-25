from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository


class OpenOrderUseCase:
    def __init__(self, repository: OrderRepository, unit_of_work: OrdersUnitOfWork) -> None:
        self._repository: OrderRepository = repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, order_id: str) -> None:
        with self._unit_of_work:
            # AnnAssign factory-born 회귀(#195): `x: T = Factory.create(...)` 도
            # Assign 과 동등하게 factory_born 으로 수집된다 — strict mypy 표기 오탐 방지.
            order: Order = Order.open_pending(order_id)
            self._repository.save(order)
