from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OrderArchived:
    order_id: str
