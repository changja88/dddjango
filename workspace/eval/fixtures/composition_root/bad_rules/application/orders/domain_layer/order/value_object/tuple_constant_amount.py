from __future__ import annotations

from dataclasses import dataclass

_ALLOWED_SCALES: tuple[int, ...] = (1, 10, 100)


@dataclass(frozen=True, slots=True)
class TupleConstantAmount:
    value: int
