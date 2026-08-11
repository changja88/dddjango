from __future__ import annotations


class RecordOrderUseCase:
    def execute(self, order_id: str) -> None:
        report = Report(order_id=order_id, source="orders")
        self._repository.save(report)
