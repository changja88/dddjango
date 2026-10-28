from __future__ import annotations

from typing import Callable


class ItemRefund:
    def __init__(self, on_retry: Callable[[int], None]) -> None:
        self._on_retry: Callable[[int], None] = on_retry

    def refund(self, item_id: int) -> None:
        self._on_retry(item_id)
