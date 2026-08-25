from __future__ import annotations


class Order:
    @classmethod
    def open_pending(cls, order_id: str) -> "Order":
        order: Order = cls()
        order._order_id = order_id
        return order

    def place(self, sku: str, qty: int) -> None:
        self._sku: str = sku
        self._qty: int = qty
