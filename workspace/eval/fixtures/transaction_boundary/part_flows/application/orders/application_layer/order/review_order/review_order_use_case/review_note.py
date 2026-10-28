from __future__ import annotations

from application.orders.domain_layer.order.order import Order

from .review_order_frame import ReviewOrderFrame


class ReviewNote:
    def __init__(self, frame: ReviewOrderFrame) -> None:
        self._frame: ReviewOrderFrame = frame

    def run(self, order_id: str) -> bool:
        order: Order = self._frame.find_order(order_id)
        return order.is_open()
