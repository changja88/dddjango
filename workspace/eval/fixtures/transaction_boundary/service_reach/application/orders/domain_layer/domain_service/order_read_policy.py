from __future__ import annotations

from application.orders.domain_layer.order.order import Order


class OrderReadPolicy:
    """칸을 읽고 예외만 낸다(루트 메서드 호출 0)."""

    @staticmethod
    def ensure(order: Order, lead: Order) -> None:
        if order.label == lead.label:
            raise ValueError(order.order_id)
