from __future__ import annotations


class OrderLine:
    def __init__(self, sku: str) -> None:
        self.sku: str = sku


class LineNote:
    def __init__(self, note: str) -> None:
        self.note: str = note
