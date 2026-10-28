from __future__ import annotations

from collections.abc import Callable

from application.orders.application_layer.port.event_publisher.event_publisher_port import EventPublisherPort
from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order_repository import OrderRepository

from .confirm_notice import ConfirmNotice
from .confirm_order_frame import ConfirmOrderFrame


class ConfirmOrderUseCase:
    def __init__(
        self,
        order_repository: OrderRepository,
        new_unit_of_work: Callable[[], OrdersUnitOfWork],
        event_publisher: EventPublisherPort,
    ) -> None:
        self._frame: ConfirmOrderFrame = ConfirmOrderFrame(order_repository, new_unit_of_work)
        self._confirm_notice: ConfirmNotice = ConfirmNotice(self._frame, event_publisher)

    def execute(self, order_id: str) -> bool:
        return self._confirm_notice.run(order_id)
