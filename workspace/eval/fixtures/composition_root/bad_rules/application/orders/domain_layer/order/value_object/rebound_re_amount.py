from __future__ import annotations

from dataclasses import dataclass
import re
from types import SimpleNamespace

re = SimpleNamespace(compile=lambda pattern: pattern)
_AMOUNT_PATTERN: re.Pattern[str] = re.compile(r"[0-9]+")


@dataclass(frozen=True, slots=True)
class ReboundReAmount:
    value: str
