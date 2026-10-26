from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TaxBand:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("세금 구간")
