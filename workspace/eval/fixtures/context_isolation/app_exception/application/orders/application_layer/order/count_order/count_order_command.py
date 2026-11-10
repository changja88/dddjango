from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CountOrderCommand:
    order_id: str
