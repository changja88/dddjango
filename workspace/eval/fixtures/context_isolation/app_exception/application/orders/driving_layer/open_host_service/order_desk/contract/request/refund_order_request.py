from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RefundOrderRequest:
    order_id: str
