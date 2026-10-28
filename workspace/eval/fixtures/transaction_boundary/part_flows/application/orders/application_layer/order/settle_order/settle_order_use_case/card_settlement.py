from __future__ import annotations

from application.orders.domain_layer.order.order import Order

from .settle_order_frame import SettleOrderFrame


class CardSettlement:
    def __init__(self, frame: SettleOrderFrame) -> None:
        self._frame: SettleOrderFrame = frame

    def prepare(self, order_id: str, amount: int) -> Order:
        order: Order = self._frame.find_order(order_id)
        order.pay(amount)
        return order

    def finish(self, order: Order) -> None:
        order.settle()
