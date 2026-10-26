from __future__ import annotations

from dataclasses import dataclass

from .percent import Percent


@dataclass(frozen=True)
class TariffFee:
    rate: Percent

    def __post_init__(self) -> None:
        if self.rate.value > 100:
            raise ValueError("요금")
