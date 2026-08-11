from __future__ import annotations


class Order:
    def refund(self) -> None:
        self._refunded: bool = True
