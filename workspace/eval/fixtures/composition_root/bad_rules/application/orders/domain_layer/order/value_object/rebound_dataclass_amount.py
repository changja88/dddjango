from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ReboundDataclassAmount:
    value: int

    def doubled(self) -> int:
        dataclass = self.value * 2
        return dataclass
