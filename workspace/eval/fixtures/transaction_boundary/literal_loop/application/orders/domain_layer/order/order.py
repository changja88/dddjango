from __future__ import annotations


class Order:
    def __init__(self, order_id: str) -> None:
        self.order_id: str = order_id
        self._state: str = "open"

    def cancel(self) -> None:
        self._state = "cancelled"

    def move_to(self, other_id: str) -> None:
        self._moved_to: str = other_id
