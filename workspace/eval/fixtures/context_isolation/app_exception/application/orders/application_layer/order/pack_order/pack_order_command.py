from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PackOrderCommand:
    order_id: str
