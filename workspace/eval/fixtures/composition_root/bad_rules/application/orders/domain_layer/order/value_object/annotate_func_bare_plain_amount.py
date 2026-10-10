from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=False)
class AnnotateFuncBarePlainAmount:
    def __annotate_func__(format):
        setattr(__class__, "create", staticmethod(lambda value: value))
        return {"value": int}

    @classmethod
    def create(cls, value: int) -> AnnotateFuncBarePlainAmount:
        return cls(value)
