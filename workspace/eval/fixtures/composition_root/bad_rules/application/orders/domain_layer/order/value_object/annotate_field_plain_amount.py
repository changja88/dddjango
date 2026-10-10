from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=False)
class AnnotateFieldPlainAmount:
    value: int

    def __annotate__(format):
        setattr(__class__, "create", staticmethod(lambda value: value))
        return {"value": int}

    def __annotations__():
        pass

    @classmethod
    def create(cls, value: int) -> AnnotateFieldPlainAmount:
        return cls(value)
