from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class FieldDefaultAmount:
    value: int = field(default=0)
