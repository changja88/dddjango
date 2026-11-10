from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RefundOrderCommand:
    order_id: str
