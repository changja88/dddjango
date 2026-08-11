from __future__ import annotations

from application.orders.domain_layer.order.event.order_placed import OrderPlaced


class SyncUseCase:
    def execute(self, fact: OrderPlaced) -> None:
        return None
