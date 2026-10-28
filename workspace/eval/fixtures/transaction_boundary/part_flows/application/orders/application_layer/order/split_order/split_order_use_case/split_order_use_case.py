from __future__ import annotations

from collections.abc import Callable

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order_repository import OrderRepository

from .split_order_frame import SplitOrderFrame
from .split_request import SplitRequest


class SplitOrderUseCase:
    def __init__(self, order_repository: OrderRepository, new_unit_of_work: Callable[[], OrdersUnitOfWork]) -> None:
        self._frame: SplitOrderFrame = SplitOrderFrame(order_repository, new_unit_of_work)
        self._split_request: SplitRequest = SplitRequest(self._frame)

    def execute(self, order_id: str) -> bool:
        return self._split_request.run(order_id)
