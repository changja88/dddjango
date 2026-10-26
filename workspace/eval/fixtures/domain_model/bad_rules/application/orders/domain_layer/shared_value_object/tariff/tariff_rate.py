from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TariffRate:
    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError("요율")


@dataclass(frozen=True)
class TariffCeiling:
    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError("상한")
