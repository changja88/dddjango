from __future__ import annotations


class Order:
    def place(self, sku: str) -> None:
        self._sku: str = sku
