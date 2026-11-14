from __future__ import annotations

from application.orders.domain_layer.order.order import Order


class NotePolicy:
    """조회 뒤 속성 너머 그릇을 바꾼다(`order.notes.append(…)`)."""

    @staticmethod
    def link(order: Order, lead: Order) -> None:
        if not order.is_open():
            raise ValueError(lead.order_id)
        order.notes.append(lead.order_id)
