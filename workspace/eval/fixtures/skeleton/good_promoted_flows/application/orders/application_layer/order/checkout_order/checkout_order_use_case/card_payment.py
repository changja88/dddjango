from __future__ import annotations

from .checkout_memory import _CheckoutMemory
from .checkout_order_frame import CheckoutOrderFrame
from .stock_hold import StockHold


class CardPayment:
    def __init__(self, frame: CheckoutOrderFrame, stock_hold: StockHold) -> None:
        self._frame: CheckoutOrderFrame = frame
        self._stock_hold: StockHold = stock_hold

    def run(self, memory: _CheckoutMemory) -> None:
        self._stock_hold.hold(memory)
        self._frame.commit_order_change(memory.order_id, change=lambda order: order.pay(100))
        self._frame.mark_paid(memory)
