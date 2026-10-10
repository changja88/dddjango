from __future__ import annotations

from dataclasses import dataclass
import re

_LANGUAGE_CODE_PATTERN: re.Pattern[str] = re.compile(r"[a-z]{2,3}(?:-[a-z0-9]+)*", re.IGNORECASE | re.ASCII)
_LANGUAGE_CODE_MAX_LENGTH: int = 35


@dataclass(frozen=True, slots=True)
class LanguageCode:
    """지원 언어 집합과 독립적인 언어 코드다."""

    value: str

    def __post_init__(self) -> None:
        if (
            type(self.value) is not str
            or len(self.value) > _LANGUAGE_CODE_MAX_LENGTH
            or not _LANGUAGE_CODE_PATTERN.fullmatch(self.value)
        ):
            raise ValueError(f"올바르지 않은 언어 코드다: {self.value!r}")
