"""bad_part_rule — 갈래 부품이 틀 읽기 도구로 받은 애그리거트의 속성에 손을 넣어 바꾼다(#257 · 부품 넓힘)."""
from __future__ import annotations

from .checkout_order_frame import CheckoutOrderFrame


class CardPayment:
    def __init__(self, frame: CheckoutOrderFrame) -> None:
        self._frame: CheckoutOrderFrame = frame

    def pay(self, order_id: str, sku: str, line: str) -> None:
        order = self._frame.find_order(order_id)
        stock = self._frame.find_stock(sku)
        order.lines.append(line)
        stock.reserve(1)
        self._frame.save_order_and_stock(order, stock)
