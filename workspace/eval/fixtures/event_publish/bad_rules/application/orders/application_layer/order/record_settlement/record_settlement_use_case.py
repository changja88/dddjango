from __future__ import annotations


class RecordSettlementUseCase:
    def execute(self, order_id: str, amount: int) -> None:
        ledger = self._repository.get(order_id)
        ledger.total += amount
        self._repository.save(ledger)
        self._broker.publish("orders.settlement_recorded")
