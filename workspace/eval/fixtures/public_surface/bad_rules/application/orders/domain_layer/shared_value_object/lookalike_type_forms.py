"""이름만 같은 생성자는 함수 꼴 타입 선언이 아니다 — 출처가 typing 계열이 아니면 #493."""
from collections.abc import Callable
from typing import TypeVar

from .labels import NewType


def TypedDict(name: str, fields: dict[str, type]) -> type:
    return type(name, (), dict(fields))


Lookalike = TypedDict("Lookalike", {"count": int})
Borrowed = NewType("Borrowed", int)
plain = 3


def shadowed(TypeVar: Callable[[str], str]) -> str:
    Shadowed = TypeVar("Shadowed")
    return Shadowed
