from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RefundDenied:
    order_id: str
