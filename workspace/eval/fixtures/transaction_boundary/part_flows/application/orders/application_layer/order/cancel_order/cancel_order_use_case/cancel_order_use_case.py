from __future__ import annotations

from collections.abc import Callable

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order_repository import OrderRepository

from .cancel_order_frame import CancelOrderFrame
from .cancel_request import CancelRequest


class CancelOrderUseCase:
    def __init__(self, order_repository: OrderRepository, new_unit_of_work: Callable[[], OrdersUnitOfWork]) -> None:
        self._frame: CancelOrderFrame = CancelOrderFrame(order_repository, new_unit_of_work)
        self._cancel_request: CancelRequest = CancelRequest(self._frame)

    def execute(self, order_id: str) -> bool:
        return self._cancel_request.run(order_id)
