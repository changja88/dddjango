from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RefundOrderResult:
    order_id: str
