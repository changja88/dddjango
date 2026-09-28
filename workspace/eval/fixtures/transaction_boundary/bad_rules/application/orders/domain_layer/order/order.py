from __future__ import annotations

from collections.abc import Sequence


class Order:
    def place(self, sku: str, qty: int) -> None:
        self._sku: str = sku
        self._qty: int = qty

    @staticmethod
    def open_among(orders: Sequence[Order]) -> tuple[Order, ...]:
        return tuple(order for order in orders if order.is_open)

    @classmethod
    def seed_batch(cls) -> tuple["Order", ...]:
        return (cls(), cls())
