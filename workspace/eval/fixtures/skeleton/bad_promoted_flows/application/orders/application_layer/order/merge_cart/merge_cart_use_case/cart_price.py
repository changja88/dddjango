from __future__ import annotations

from .cart_tax import CartTax
from .merge_cart_frame import MergeCartFrame


class CartPrice:
    def __init__(self, frame: MergeCartFrame, cart_tax: CartTax) -> None:
        self._frame: MergeCartFrame = frame
        self._cart_tax: CartTax = cart_tax

    def total(self, cart_id: int) -> int:
        self._frame.record_done(cart_id)
        return 100 + self._cart_tax.tax(cart_id, self)
