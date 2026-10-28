from __future__ import annotations

from collections.abc import Callable

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order_repository import OrderRepository

from .hold_order_frame import HoldOrderFrame
from .order_hold import OrderHold


class HoldOrderUseCase:
    def __init__(self, order_repository: OrderRepository, new_unit_of_work: Callable[[], OrdersUnitOfWork]) -> None:
        self._order_repository: OrderRepository = order_repository
        self._frame: HoldOrderFrame = HoldOrderFrame(order_repository, new_unit_of_work)
        self._order_hold: OrderHold = OrderHold(self._frame)

    def execute(self, order_id: str) -> bool:
        return self._order_hold.run(self._order_repository, order_id)
