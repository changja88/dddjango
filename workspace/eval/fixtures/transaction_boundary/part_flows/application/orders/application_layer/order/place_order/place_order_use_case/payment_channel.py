from __future__ import annotations


class _PaymentChannel:
    def __init__(self, order_id: str) -> None:
        self._order_id: str = order_id
        self._open: bool = True

    def close(self) -> None:
        self._open = False
