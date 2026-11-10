from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CancelOrderRequest:
    order_id: str
