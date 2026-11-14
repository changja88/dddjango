from __future__ import annotations

from application.orders.domain_layer.order.order import Order


class LeadStamp:
    @staticmethod
    def stamp(target: Order, lead_id: int) -> None:
        target.lead_id = lead_id
