from __future__ import annotations

from dataclasses import dataclass

classmethod = staticmethod


@dataclass(frozen=True)
class StaticmethodAliasAmount:
    value: int

    @classmethod
    def create(cls, value: int) -> StaticmethodAliasAmount:
        return cls(value)
