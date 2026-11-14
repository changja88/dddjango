from __future__ import annotations

from application.orders.domain_layer.order.value_object.terms import Terms


class Order:
    def __init__(self, order_id: int, label: str) -> None:
        self.order_id: int = order_id
        self.label: str = label
        self.lead_id: int | None = None
        self.revision: int = 0
        self.notes: list[int] = []
        self.tags: dict[str, int] = {}
        self.terms: Terms = Terms()

    def link_to(self, lead_id: int) -> None:
        self.lead_id = lead_id

    def is_open(self) -> bool:
        return True
