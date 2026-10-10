from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ParcelWeight:
    """소포 무게(그램)다(통과 모듈 — 재료 이름 `settings` 반례의 짝)."""

    grams: int

    def __post_init__(self) -> None:
        if self.grams <= 0:
            raise ValueError("무게는 0 보다 크다")
