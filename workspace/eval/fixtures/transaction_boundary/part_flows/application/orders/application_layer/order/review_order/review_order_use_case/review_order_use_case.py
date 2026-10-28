from __future__ import annotations

from collections.abc import Callable

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order_repository import OrderRepository

from .review_note import ReviewNote
from .review_order_frame import ReviewOrderFrame


class ReviewOrderUseCase:
    def __init__(self, order_repository: OrderRepository, new_unit_of_work: Callable[[], OrdersUnitOfWork]) -> None:
        self._frame: ReviewOrderFrame = ReviewOrderFrame(order_repository, new_unit_of_work)
        self._review_note: ReviewNote = ReviewNote(self._frame)

    def execute(self, order_id: str) -> bool:
        return self._review_note.run(order_id)
