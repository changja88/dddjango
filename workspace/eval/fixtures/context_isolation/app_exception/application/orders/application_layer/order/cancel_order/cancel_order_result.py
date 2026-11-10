from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CancelOrderResult:
    order_id: str
