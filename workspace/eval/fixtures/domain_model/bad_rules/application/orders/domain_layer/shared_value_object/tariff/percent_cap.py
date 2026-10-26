from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PercentCap:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("상한 비율")
