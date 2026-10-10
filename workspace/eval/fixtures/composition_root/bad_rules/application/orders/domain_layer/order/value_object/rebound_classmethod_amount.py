from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ReboundClassmethodAmount:
    value: int

    def doubled(self) -> int:
        classmethod = self.value * 2
        return classmethod
