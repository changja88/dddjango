from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Currency:
    code: str

    def __post_init__(self) -> None:
        if len(self.code) != 3:
            raise ValueError("통화")
