from __future__ import annotations


class Order:
    def place(self, sku: str, qty: int) -> None:
        self._sku: str = sku
        self._qty: int = qty
