"""갈래 부품 — 틀의 공개 메서드로만 읽고 쓴다."""
from __future__ import annotations

from application.orders.domain_layer.order.order import Order

from .checkout_order_frame import CheckoutOrderFrame


class CardPayment:
    def __init__(self, frame: CheckoutOrderFrame) -> None:
        self._frame: CheckoutOrderFrame = frame

    def pay(self, order_id: str) -> None:
        order: Order = self._frame.load_order(order_id)
        order.pay()
        self._frame.commit_order(order)
