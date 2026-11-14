from __future__ import annotations

from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.domain_service.lead_stamp import LeadStamp


class SiblingStampPolicy:
    """조회 뒤 형제 서비스에 넘겨 칸을 바꾼다."""

    @staticmethod
    def link(order: Order, lead: Order) -> None:
        if not order.is_open():
            raise ValueError(lead.order_id)
        LeadStamp.stamp(order, lead.order_id)
