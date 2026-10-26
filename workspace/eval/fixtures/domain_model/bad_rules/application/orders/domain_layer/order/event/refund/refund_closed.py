from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RefundClosed:
    order_id: str
