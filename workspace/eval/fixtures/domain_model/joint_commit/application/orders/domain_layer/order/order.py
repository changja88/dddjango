from __future__ import annotations


class Order:
    def __init__(self, order_id: str) -> None:
        self.order_id: str = order_id
        self.label: str = ""
        self._state: str = "open"

    def cancel(self) -> None:
        self._state = "cancelled"
        self._ensure_valid()

    def move_to(self, other: str) -> None:
        self.label = other
        self._ensure_valid()

    def _ensure_valid(self) -> None:
        return None
