from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RefundIssued:
    order_id: str

    def describe(self) -> str:
        return self.order_id
