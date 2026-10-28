from __future__ import annotations

from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository

from .hold_order_frame import HoldOrderFrame


class OrderHold:
    def __init__(self, frame: HoldOrderFrame) -> None:
        self._frame: HoldOrderFrame = frame

    def run(self, order_repository: OrderRepository, order_id: str) -> bool:
        order: Order = order_repository.get(order_id)
        if not order.is_open():
            return False
        return self._frame.commit_order_change(order_id, lambda current: current.hold())
