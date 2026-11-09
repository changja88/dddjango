from __future__ import annotations

from typing import TypeAlias

Row: TypeAlias = "dict[str, int | str]"


def heading(text: str, words: list[str]) -> str:
    return text.title() + "-".join(words) + str(len(words)).replace("0", "o")


def has_nonzero(numbers: list[int]) -> bool:
    return any(numbers)


def row_names(row: Row) -> list[str]:
    return [name.title() for name, _ in row.items()]


def nonempty(numbers: list[int]) -> bool:
    return bool(numbers)


def capitalized(lines: list[str]) -> list[str]:
    return list(map(str.title, lines))
