from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LateConstantAmount:
    value: int


_SCALE: int = 100
