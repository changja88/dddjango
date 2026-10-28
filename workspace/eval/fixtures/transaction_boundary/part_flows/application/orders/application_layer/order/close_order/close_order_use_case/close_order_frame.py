from __future__ import annotations

from collections.abc import Callable

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository


class CloseOrderFrame:
    def __init__(self, order_repository: OrderRepository, new_unit_of_work: Callable[[], OrdersUnitOfWork]) -> None:
        self._order_repository: OrderRepository = order_repository
        self._new_unit_of_work: Callable[[], OrdersUnitOfWork] = new_unit_of_work

    def find_order(self, order_id: str) -> Order:
        return self._order_repository.get(order_id)

    def save_order(self, order: Order) -> None:
        self._order_repository.save(order)

    def run_in_unit_of_work(self, work: Callable[[], None]) -> None:
        with self._new_unit_of_work():
            work()

    def run_with_unit_of_work(self, work) -> None:
        with self._new_unit_of_work():
            work()
