from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository


class SplitOrderFrame:
    def __init__(self, order_repository: OrderRepository, new_unit_of_work: Callable[[], OrdersUnitOfWork]) -> None:
        self._order_repository: OrderRepository = order_repository
        self._new_unit_of_work: Callable[[], OrdersUnitOfWork] = new_unit_of_work

    def find_order(self, order_id: str) -> Order:
        return self._order_repository.get(order_id)

    def save_order(self, order: Order) -> None:
        self._order_repository.save(order)

    @contextmanager
    def transaction(self) -> Iterator[None]:
        with self._new_unit_of_work():
            yield
