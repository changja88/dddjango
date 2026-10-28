from __future__ import annotations

from collections.abc import Callable

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository


class RenewOrderFrame:
    def __init__(self, order_repository: OrderRepository, new_unit_of_work: Callable[[], OrdersUnitOfWork]) -> None:
        self._order_repository: OrderRepository = order_repository
        self._new_unit_of_work: Callable[[], OrdersUnitOfWork] = new_unit_of_work

    def commit_order_change(self, order_id: str, change) -> bool:
        with self._new_unit_of_work():
            order: Order = self._order_repository.get(order_id)
            if not change(order):
                return False
            self._order_repository.save(order)
            return True
