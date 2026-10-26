from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DiscountFloor:
    amount: int

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("할인 금액")
