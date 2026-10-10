from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AnnotationsMethodAmount:
    value: int

    def __annotations__():
        pass
