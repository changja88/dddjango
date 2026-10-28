from __future__ import annotations

from .checkout_memory import _CheckoutMemory
from .checkout_order_frame import CheckoutOrderFrame


class StockHold:
    def __init__(self, frame: CheckoutOrderFrame) -> None:
        self._frame: CheckoutOrderFrame = frame

    def hold(self, memory: _CheckoutMemory) -> None:
        self._frame.commit_order_change(memory.order_id, change=lambda order: order.hold_stock())
