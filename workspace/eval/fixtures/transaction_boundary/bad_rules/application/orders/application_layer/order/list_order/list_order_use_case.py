from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork


class ListOrderUseCase:
    def __init__(self, unit_of_work: OrdersUnitOfWork) -> None:
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, unit_of_work: OrdersUnitOfWork) -> list:
        return []
