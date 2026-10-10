from __future__ import annotations

from dataclasses import dataclass

_PATCHED: None = setattr(dataclass, "__doc__", "patched")


@dataclass(frozen=True, slots=True)
class SetattrConstantAmount:
    value: int
