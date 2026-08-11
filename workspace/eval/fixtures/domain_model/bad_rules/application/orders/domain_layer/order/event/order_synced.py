from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OrderSynced:
    order_id: str
