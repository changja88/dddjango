from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetryOrderResult:
    order_id: str
