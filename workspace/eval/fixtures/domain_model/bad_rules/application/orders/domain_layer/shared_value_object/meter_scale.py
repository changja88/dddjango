from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MeterScale:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("계량")
