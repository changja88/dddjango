from __future__ import annotations

from typing import Callable

from application.orders.application_layer.port.unit_of_work.order_unit_of_work import OrderUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository

from .checkout_memory import _CheckoutMemory


class CheckoutOrderFrame:
    def __init__(self, order_repository: OrderRepository,
                 new_unit_of_work: Callable[[], OrderUnitOfWork]) -> None:
        self._order_repository: OrderRepository = order_repository
        self._new_unit_of_work: Callable[[], OrderUnitOfWork] = new_unit_of_work

    def find_order(self, order_id: int) -> Order:
        return self._order_repository.find_by_id(order_id)

    def commit_order_change(self, order_id: int, change: Callable[[Order], bool]) -> None:
        with self._new_unit_of_work():
            order: Order = self._order_repository.find_by_id(order_id)
            if change(order):
                self._order_repository.save(order)

    def mark_paid(self, memory: _CheckoutMemory) -> None:
        memory.paid = True
