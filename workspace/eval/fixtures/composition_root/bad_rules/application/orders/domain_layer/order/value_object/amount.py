from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Amount:
    """주문 금액이다(통과 모듈 — 재료 `def Amount()` 가림 반례의 짝)."""

    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError("금액은 0 이상이다")
