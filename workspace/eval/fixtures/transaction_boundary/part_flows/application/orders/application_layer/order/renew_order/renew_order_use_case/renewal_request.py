from __future__ import annotations

from application.orders.domain_layer.order.order import Order

from .renew_order_frame import RenewOrderFrame


class RenewalRequest:
    def __init__(self, frame: RenewOrderFrame) -> None:
        self._frame: RenewOrderFrame = frame

    def run(self, order_id: str) -> bool:
        return self._frame.commit_order_change(order_id, Order.renew)
