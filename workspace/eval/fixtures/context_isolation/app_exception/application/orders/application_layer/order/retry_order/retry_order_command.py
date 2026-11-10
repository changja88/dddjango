from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetryOrderCommand:
    order_id: str
