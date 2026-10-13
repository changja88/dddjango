from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ShipmentCompleted:
    sku: str

    def __post_init__(self) -> None:
        if not self.sku:
            raise ValueError("sku")
