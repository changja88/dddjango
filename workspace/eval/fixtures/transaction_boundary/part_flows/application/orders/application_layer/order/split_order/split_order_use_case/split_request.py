from __future__ import annotations

from application.orders.domain_layer.order.order import Order

from .split_order_frame import SplitOrderFrame


class SplitRequest:
    def __init__(self, frame: SplitOrderFrame) -> None:
        self._frame: SplitOrderFrame = frame

    def run(self, order_id: str) -> bool:
        with self._frame.transaction():
            order: Order = self._frame.find_order(order_id)
            if not order.split():
                return False
            self._frame.save_order(order)
        return True
