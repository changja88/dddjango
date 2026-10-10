from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=False)
class AnnotateBarePlainAmount:
    def __annotate__(format):
        setattr(__class__, "create", staticmethod(lambda value: value))
        return {"value": int}

    @classmethod
    def create(cls, value: int) -> AnnotateBarePlainAmount:
        return cls(value)
