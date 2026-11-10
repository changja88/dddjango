from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RefundOrderResponse:
    order_id: str
