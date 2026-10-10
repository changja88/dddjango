from __future__ import annotations

from dataclasses import dataclass

SCALE: int = 100


@dataclass(frozen=True, slots=True)
class PublicConstantAmount:
    value: int
