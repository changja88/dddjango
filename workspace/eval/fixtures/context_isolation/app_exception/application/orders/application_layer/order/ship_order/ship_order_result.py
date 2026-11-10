from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ShipOrderResult:
    order_id: str
