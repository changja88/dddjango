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

    @staticmethod
    def kept(order: Order) -> Order:
        return order

    @classmethod
    def retouched(cls, orders: Sequence[Order]) -> tuple[Order, ...]:
        return tuple(cls.kept(order) for order in orders)

    @classmethod
    def merged_with(cls, orders: Sequence[Order]) -> list[Order]:
        batch: list[Order] = [cls()]
        batch.extend(orders)
        return batch

    @classmethod
    def with_followup(cls, orders: Sequence[Order]) -> list[Order]:
        batch: list[Order] = list(orders)
        batch.append(cls())
        return batch
