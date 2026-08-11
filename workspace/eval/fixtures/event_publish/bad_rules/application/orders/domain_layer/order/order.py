from __future__ import annotations


class Order:
    def reduce(self, qty: int) -> None:
        self._qty: int = qty

    def place(self, sku: str) -> None:
        self._sku: str = sku
