from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StockReduced:
    order_id: str
