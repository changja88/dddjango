from __future__ import annotations


class OrderLine:
    def __init__(self, line_id: str, sku: str) -> None:
        self.line_id: str = line_id
        self.sku: str = sku
