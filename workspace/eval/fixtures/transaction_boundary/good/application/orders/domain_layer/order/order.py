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

    @classmethod
    def seed_batch(cls) -> tuple["Order", ...]:
        return (cls.open_pending("seed-1"), cls.open_pending("seed-2"))

    @staticmethod
    def ensure_distinct_ids(orders: tuple["Order", ...]) -> None:
        order_ids: set[str] = {order._order_id for order in orders}
        if len(order_ids) != len(orders):
            raise ValueError("주문 식별자가 겹친다")

    @classmethod
    def open_batch(cls, order_ids: tuple[str, ...]) -> tuple["Order", ...]:
        orders: list[Order] = []
        order_id: str
        for order_id in order_ids:
            orders.append(cls.open_pending(order_id))
        return tuple(orders)
