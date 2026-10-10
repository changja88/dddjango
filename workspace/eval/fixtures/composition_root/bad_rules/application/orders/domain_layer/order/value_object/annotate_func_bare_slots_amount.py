from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AnnotateFuncBareSlotsAmount:
    def __annotate_func__(format):
        setattr(__class__, "create", staticmethod(lambda value: value))
        return {"value": int}

    @classmethod
    def create(cls, value: int) -> AnnotateFuncBareSlotsAmount:
        return cls(value)
