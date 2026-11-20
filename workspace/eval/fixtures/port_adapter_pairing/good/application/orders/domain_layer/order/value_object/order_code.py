from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OrderCode:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("주문 코드가 비었다")
