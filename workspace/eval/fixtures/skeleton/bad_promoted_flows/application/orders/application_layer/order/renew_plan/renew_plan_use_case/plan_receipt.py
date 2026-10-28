from __future__ import annotations

from typing import Callable


class PlanReceipt:
    def __init__(self, on_reissue: Callable[[int], None]) -> None:
        self._on_reissue: Callable[[int], None] = on_reissue

    def issue(self, plan_id: int) -> None:
        self._on_reissue(plan_id)
