from __future__ import annotations


class Order:
    def __init__(self, order_id: str) -> None:
        self.order_id: str = order_id
        self._state: str = "open"

    @classmethod
    def open(cls, order_id: str) -> Order:
        return cls(order_id)

    def is_open(self) -> bool:
        return self._state == "open"

    def cancel(self) -> None:
        self._state = "cancelled"
        self._ensure_valid()

    def rename(self, label: str) -> None:
        self._label: str = label
        self._ensure_valid()

    def _ensure_valid(self) -> None:
        return None
