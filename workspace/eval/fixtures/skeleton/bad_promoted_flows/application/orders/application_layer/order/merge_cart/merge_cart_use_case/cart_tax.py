from __future__ import annotations

from .cart_price import CartPrice
from .merge_cart_frame import MergeCartFrame


class CartTax:
    def __init__(self, frame: MergeCartFrame) -> None:
        self._frame: MergeCartFrame = frame

    def tax(self, cart_id: int, price: CartPrice) -> int:
        return cart_id % 10
