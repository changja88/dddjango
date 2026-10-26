from __future__ import annotations

from dataclasses import dataclass

from .discount_floor import DiscountFloor


@dataclass(frozen=True)
class DiscountRate:
    percent: int
    floor: DiscountFloor

    def __post_init__(self) -> None:
        if not 0 <= self.percent <= 100:
            raise ValueError("할인율")
