from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PropertyAmount:
    value: int

    @property
    def doubled(self) -> int:
        return self.value * 2
