from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CancelOrderCommand:
    order_id: str
