from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HoldOrderResult:
    order_id: str
