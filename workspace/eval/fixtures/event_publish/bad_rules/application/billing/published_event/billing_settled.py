from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BillingSettled:
    order_id: str
    amount: int
