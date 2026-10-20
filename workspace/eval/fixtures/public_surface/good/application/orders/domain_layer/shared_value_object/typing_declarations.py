"""함수 꼴 타입 선언 — 그 대입이 곧 타입 선언이라 주석을 달 문법이 없다(R-3667)."""
import typing
import typing as t
from typing import NamedTuple, NewType, ParamSpec, TypedDict, TypeVar, TypeVarTuple
from typing import TypedDict as _TypedDict

ShelfArguments = TypedDict("ShelfArguments", {"pass": bool, "count": int})
AliasedArguments = _TypedDict("AliasedArguments", {"pass": bool})
PrefixedArguments = typing.TypedDict("PrefixedArguments", {"pass": bool})
ShelfSpan = NamedTuple("ShelfSpan", [("start", int), ("end", int)])
ShelfId = NewType("ShelfId", int)
ModuleAliasId = t.NewType("ModuleAliasId", int)
T = TypeVar("T")
P = ParamSpec("P")
Ts = TypeVarTuple("Ts")


def shelf_kind() -> str:
    """함수 본문의 함수 꼴 선언도 같다."""
    Local = NamedTuple("Local", [("kind", str)])
    return Local("shelf").kind
