from __future__ import annotations

from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository

from .pay_order_frame import PayOrderFrame


class CardPayment:
    def __init__(self, frame: PayOrderFrame, order_repository: OrderRepository) -> None:
        self._frame: PayOrderFrame = frame
        self._order_repository: OrderRepository = order_repository

    def run(self, order_id: str, amount: int) -> bool:
        order: Order = self._order_repository.get(order_id)
        if not order.is_open():
            return False
        return self._frame.commit_order_change(order_id, lambda current: current.pay(amount))
