from __future__ import annotations

from application.orders.domain_layer.order.order import Order

from .cancel_order_frame import CancelOrderFrame


class CancelRequest:
    def __init__(self, frame: CancelOrderFrame) -> None:
        self._frame: CancelOrderFrame = frame

    def run(self, order_id: str) -> bool:
        order: Order = self._frame.order_repository.get(order_id)
        if not order.is_open():
            return False
        return self._frame.commit_order_change(order_id, lambda current: current.cancel())
