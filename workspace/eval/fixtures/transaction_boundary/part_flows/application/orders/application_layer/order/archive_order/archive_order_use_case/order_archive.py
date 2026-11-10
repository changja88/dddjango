from __future__ import annotations

from application.orders.domain_layer.order.order import Order

from .archive_order_frame import ArchiveOrderFrame


class OrderArchive:
    def __init__(self, frame: ArchiveOrderFrame) -> None:
        self._frame: ArchiveOrderFrame = frame

    def run(self, order_id: str) -> bool:
        order: Order = self._frame.find_order(order_id)
        if not order.archive():
            return False
        self._frame.save_order(order)
        return True
