from __future__ import annotations

from dataclasses import dataclass
from functools import total_ordering


@dataclass(frozen=True)
@total_ordering
class DoubleDecoratorAmount:
    value: int
