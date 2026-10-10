from __future__ import annotations

from dataclasses import dataclass
from decimal import getcontext


def _replace(cls: type) -> object:
    return getcontext


@_replace
@dataclass(frozen=True)
class ReplacedAmount:
    value: int = 0
