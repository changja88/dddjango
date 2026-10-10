from __future__ import annotations

from dataclasses import dataclass


def dataclass(*args: object, **kwargs: object) -> object:
    return lambda cls: cls


@dataclass(frozen=True)
class ShadowedDataclassAmount:
    value: int
