from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LimitAmount:
    """주문 한도 금액이다."""

    value: int

    def __post_init__(self) -> None:
        if type(self.value) is not int or self.value <= 0:
            raise ValueError(f"올바르지 않은 한도 금액다: {self.value!r}")
