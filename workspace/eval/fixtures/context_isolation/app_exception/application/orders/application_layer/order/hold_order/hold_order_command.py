from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HoldOrderCommand:
    order_id: str
