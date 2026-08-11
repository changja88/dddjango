from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Money:
    money_id: str
    amount: int

    def set_amount(self, amount: int) -> None:
        self.amount = amount


@dataclass(frozen=True)
class Rate:
    value: int
