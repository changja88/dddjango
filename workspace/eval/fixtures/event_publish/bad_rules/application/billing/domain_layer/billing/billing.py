from __future__ import annotations


class Billing:
    def settle(self, amount: int) -> None:
        self._amount: int = amount
