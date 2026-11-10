from __future__ import annotations


class Stock:
    def __init__(self, sku: str) -> None:
        self.sku: str = sku
        self.reserved: int = 0

    def reserve(self, quantity: int) -> None:
        self.reserved += quantity
        self._ensure_valid()

    def _ensure_valid(self) -> None:
        return None
