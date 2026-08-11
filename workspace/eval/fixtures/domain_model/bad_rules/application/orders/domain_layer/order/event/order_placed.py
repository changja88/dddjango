from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OrderPlaced:
    order_id: str

    def as_dict(self) -> dict:
        return {}


@dataclass(frozen=True)
class OrderPlacedTwice:
    order_id: str
