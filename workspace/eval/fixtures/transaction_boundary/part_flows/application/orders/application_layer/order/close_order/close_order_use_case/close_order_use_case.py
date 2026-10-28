from __future__ import annotations

from collections.abc import Callable

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order_repository import OrderRepository

from .close_order_frame import CloseOrderFrame
from .close_request import CloseRequest


class CloseOrderUseCase:
    def __init__(self, order_repository: OrderRepository, new_unit_of_work: Callable[[], OrdersUnitOfWork]) -> None:
        self._frame: CloseOrderFrame = CloseOrderFrame(order_repository, new_unit_of_work)
        self._close_request: CloseRequest = CloseRequest(self._frame)

    def execute(self, order_id: str) -> bool:
        return self._close_request.run(order_id)
