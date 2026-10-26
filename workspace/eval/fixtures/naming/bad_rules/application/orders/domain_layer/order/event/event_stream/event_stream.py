from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EventStream:
    order_id: str
