from __future__ import annotations

from .checkout_order_frame import CheckoutOrderFrame


class CardPayment:
    def __init__(self, frame: CheckoutOrderFrame) -> None:
        self._frame: CheckoutOrderFrame = frame

    def run(self, order_id: str, amount: int) -> bool:
        return self._frame.commit_order_change(order_id, lambda order: order.pay(amount))
