from __future__ import annotations


class _PaymentChannel:
    def __init__(self, fee_id: int) -> None:
        self._fee_id: int = fee_id

    def send(self, amount: int) -> bool:
        return amount > 0
