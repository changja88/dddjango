from __future__ import annotations

from application.orders.domain_layer.order.order import Order

from .close_order_frame import CloseOrderFrame


class CloseRequest:
    def __init__(self, frame: CloseOrderFrame) -> None:
        self._frame: CloseOrderFrame = frame

    def run(self, order_id: str) -> bool:
        self._frame.run_in_unit_of_work(lambda: self._close(order_id))
        return True

    def _close(self, order_id: str) -> None:
        order: Order = self._frame.find_order(order_id)
        if order.close():
            self._frame.save_order(order)
