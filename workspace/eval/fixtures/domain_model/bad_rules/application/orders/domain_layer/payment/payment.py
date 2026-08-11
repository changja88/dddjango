from __future__ import annotations


class Payment:
    def __init__(self, payment_id: str) -> None:
        self.payment_id: str = payment_id
        self._events: list = []

    def capture(self) -> None:
        self._events.append("captured")
