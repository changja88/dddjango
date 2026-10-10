from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NewAmount:
    value: int

    def __new__(cls, *args: object, **kwargs: object) -> object:
        return 7
