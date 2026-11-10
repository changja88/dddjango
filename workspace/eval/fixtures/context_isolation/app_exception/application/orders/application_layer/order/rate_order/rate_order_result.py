from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RateOrderResult:
    order_id: str
