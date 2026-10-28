"""갈래 부품 — 틀의 공개 메서드로만 읽고 쓴다."""
from __future__ import annotations

from application.orders.domain_layer.order.order import Order

from .pay_order_frame import PayOrderFrame


class CardCharge:
    def __init__(self, frame: PayOrderFrame) -> None:
        self._frame: PayOrderFrame = frame

    def charge(self, order_id: str) -> None:
        order: Order = self._frame.load_order(order_id)
        order.pay()
        self._frame.commit_order(order)
