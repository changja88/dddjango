from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AnnotateFieldSlotsAmount:
    value: int

    def __annotate__(format):
        setattr(__class__, "create", staticmethod(lambda value: value))
        return {"value": int}

    def __annotations__():
        pass

    @classmethod
    def create(cls, value: int) -> AnnotateFieldSlotsAmount:
        return cls(value)
