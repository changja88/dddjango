from __future__ import annotations

from application.orders.domain_layer.order.order import Order


class OrderQueryPolicy:
    """조회 메서드만 부른다(`is_open()`) — 유스케이스 지역 판정과 같은 너그러움."""

    @staticmethod
    def ensure(order: Order, lead: Order) -> None:
        if not order.is_open():
            raise ValueError(lead.order_id)
