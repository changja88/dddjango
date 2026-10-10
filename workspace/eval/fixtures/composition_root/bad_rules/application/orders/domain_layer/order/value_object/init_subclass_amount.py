from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class InitSubclassAmount:
    value: int

    def __init_subclass__(cls) -> None:
        setattr(cls, "create", staticmethod(lambda value: value))
