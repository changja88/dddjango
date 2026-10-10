from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DoubleCreateAmount:
    value: int

    @classmethod
    def create(cls, value: int) -> DoubleCreateAmount:
        return cls(value)

    @classmethod
    def create(cls, value: int) -> int:
        return value
