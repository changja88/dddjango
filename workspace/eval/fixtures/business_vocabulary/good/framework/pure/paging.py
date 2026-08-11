from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Page:
    number: int
    size: int
