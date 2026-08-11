from __future__ import annotations

from application.orders.published_event.order_placed import OrderPlaced


class ApplyFactUseCase:
    def execute(self, event: OrderPlaced) -> None:
        inventory = self._repository.get(event.order_id)
        inventory.apply(event)
        self._audit.record(event)
