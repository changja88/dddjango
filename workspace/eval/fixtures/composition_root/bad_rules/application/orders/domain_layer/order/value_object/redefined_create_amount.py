from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RedefinedCreateAmount:
    value: int

    @classmethod
    def create(cls, value: int) -> RedefinedCreateAmount:
        return cls(value)

    @staticmethod
    def create(value: int) -> int:
        return value
