from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlaceOrderRequest:
    order_id: str
