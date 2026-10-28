from __future__ import annotations

from application.orders.domain_layer.order.order import Order

from .merge_orders_frame import MergeOrdersFrame


class OrderMerge:
    def __init__(self, frame: MergeOrdersFrame) -> None:
        self._frame: MergeOrdersFrame = frame

    def run(self, source_id: str, target_id: str) -> bool:
        source: Order = self._frame.find_order(source_id)
        target: Order = self._frame.find_order(target_id)
        if not source.merge_into(target):
            return False
        self._frame.save_orders_together((source, target))
        return True
