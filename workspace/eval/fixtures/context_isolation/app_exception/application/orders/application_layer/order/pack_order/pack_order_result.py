from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PackOrderResult:
    order_id: str
