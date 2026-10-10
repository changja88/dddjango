from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SetNameAmount:
    value: int

    def __set_name__(self, owner: type, name: str) -> None:
        setattr(owner, "create", staticmethod(lambda value: value))
