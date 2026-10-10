from __future__ import annotations

from dataclasses import dataclass
import re

_AMOUNT_PATTERN_TEXT: str = r"[0-9]+"
_AMOUNT_PATTERN: re.Pattern[str] = re.compile(_AMOUNT_PATTERN_TEXT)


@dataclass(frozen=True, slots=True)
class VariablePatternAmount:
    value: str
