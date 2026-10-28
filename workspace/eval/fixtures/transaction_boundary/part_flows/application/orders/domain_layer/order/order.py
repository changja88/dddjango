from __future__ import annotations


class Order:
    def __init__(self, order_id: str) -> None:
        self.order_id: str = order_id
        self._state: str = "open"
        self._paid: int = 0

    def is_open(self) -> bool:
        return self._state == "open"

    def pay(self, amount: int) -> bool:
        if not self.is_open() or amount <= 0:
            return False
        self._paid += amount
        return True

    def hold(self) -> bool:
        return self._move("open", "held")

    def ship(self) -> bool:
        return self._move("open", "shipped")

    def refund(self) -> bool:
        return self._move("open", "refunded")

    def cancel(self) -> bool:
        return self._move("open", "cancelled")

    def confirm(self) -> bool:
        return self._move("open", "confirmed")

    def close(self) -> bool:
        return self._move("open", "closed")

    def split(self) -> bool:
        return self._move("open", "split")

    def renew(self) -> bool:
        return self._move("closed", "open")

    def settle(self) -> bool:
        return self._move("open", "settled")

    def merge_into(self, other: Order) -> bool:
        if not (self.is_open() and other.is_open()):
            return False
        other._paid += self._paid
        self._paid = 0
        return self._move("open", "merged")

    def _move(self, before: str, after: str) -> bool:
        if self._state != before:
            return False
        self._state = after
        return True
