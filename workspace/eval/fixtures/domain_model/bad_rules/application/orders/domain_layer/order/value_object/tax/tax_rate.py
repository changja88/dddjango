from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TaxRate:
    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError("세율")

    def set_value(self, value: int) -> None:
        self.value = value
