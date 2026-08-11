from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    amount: int

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("음수 금액")
