from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RateOrderCommand:
    order_id: str
