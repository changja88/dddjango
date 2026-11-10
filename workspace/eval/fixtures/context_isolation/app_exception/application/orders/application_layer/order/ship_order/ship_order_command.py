from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ShipOrderCommand:
    order_id: str
