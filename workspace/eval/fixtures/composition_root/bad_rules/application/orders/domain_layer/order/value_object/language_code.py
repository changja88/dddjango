from __future__ import annotations

from dataclasses import dataclass
import re

_LANGUAGE_CODE_PATTERN: re.Pattern[str] = re.compile(r"[a-z]{2,3}(?:-[a-z0-9]+)*")


@dataclass(frozen=True, slots=True)
class LanguageCode:
    """언어 코드다(통과 모듈 · `create` 없음 — (라) `LanguageCode.create(…)` 반례의 짝 · lead 검토 (c))."""

    value: str

    def __post_init__(self) -> None:
        if type(self.value) is not str or not _LANGUAGE_CODE_PATTERN.fullmatch(self.value):
            raise ValueError(f"올바르지 않은 언어 코드다: {self.value!r}")
