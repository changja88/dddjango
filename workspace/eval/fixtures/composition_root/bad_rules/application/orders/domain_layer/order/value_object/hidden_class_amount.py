from __future__ import annotations

from dataclasses import dataclass

if True:
    class Other:
        pass


@dataclass(frozen=True)
class HiddenClassAmount:
    value: int
