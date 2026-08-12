from __future__ import annotations


class RecordOrderUseCase:
    def execute(self, order_id: str) -> None:
        billing = self._repository.get(order_id)
        billing.settle(1)
        self._repository.save(billing)
