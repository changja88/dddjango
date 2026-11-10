from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository


class Conflict(Exception):
    pass


class FrameSwapFrame:
    def __init__(self, order_repository: OrderRepository, unit_of_work: OrdersUnitOfWork) -> None:
        self._order_repository: OrderRepository = order_repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def move(self, order_id: str, other_id: str) -> None:
        with self._unit_of_work:
            source: Order = self._order_repository.get(order_id)
            target: Order = self._order_repository.get(other_id)
            source.cancel()
            target.move_to(source.order_id)
            for order in sorted((source, target), key=lambda item: item.order_id):
                if not self._order_repository.save_with_version_guard(order):
                    raise Conflict()
