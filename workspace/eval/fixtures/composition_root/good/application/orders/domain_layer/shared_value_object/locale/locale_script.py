from __future__ import annotations

from dataclasses import dataclass
import re

_LOCALE_SCRIPT_PATTERN: re.Pattern[str] = re.compile(r"[a-z]{2,8}", re.IGNORECASE | re.ASCII)


@dataclass(frozen=True, slots=True)
class LocaleScript:
    """지역 문자 체계다."""

    value: str

    def __post_init__(self) -> None:
        if type(self.value) is not str or not _LOCALE_SCRIPT_PATTERN.fullmatch(self.value):
            raise ValueError(f"올바르지 않은 문자 체계다: {self.value!r}")
