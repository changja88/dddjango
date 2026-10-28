from __future__ import annotations


class Order:
    def __init__(self, order_id: str) -> None:
        self.order_id: str = order_id
        self.lines: list = []

    def add_line(self, line: str) -> None:
        self.lines.append(line)
        self._ensure_valid()

    def _ensure_valid(self) -> None:
        return None
