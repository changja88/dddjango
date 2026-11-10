from __future__ import annotations


class OrderRejection(Exception):
    def __init__(self, order_id: str) -> None:
        super().__init__(order_id)
        self.order_id: str = order_id
