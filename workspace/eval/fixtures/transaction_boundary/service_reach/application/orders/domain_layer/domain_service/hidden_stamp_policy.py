from __future__ import annotations

from application.orders.domain_layer.order.order import Order


def _stamp(target: Order, lead_id: int) -> None:
    target.lead_id = lead_id


class HiddenStampPolicy:
    """조회 뒤 모듈 도우미에 넘겨 칸을 바꾼다."""

    @staticmethod
    def link(order: Order, lead: Order) -> None:
        if not order.is_open():
            raise ValueError(lead.order_id)
        _stamp(order, lead.order_id)
