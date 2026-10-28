from __future__ import annotations

from collections.abc import Callable

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order_repository import OrderRepository

from .renew_order_frame import RenewOrderFrame
from .renewal_request import RenewalRequest


class RenewOrderUseCase:
    def __init__(self, order_repository: OrderRepository, new_unit_of_work: Callable[[], OrdersUnitOfWork]) -> None:
        self._frame: RenewOrderFrame = RenewOrderFrame(order_repository, new_unit_of_work)
        self._renewal_request: RenewalRequest = RenewalRequest(self._frame)

    def execute(self, order_id: str) -> bool:
        return self._renewal_request.run(order_id)
