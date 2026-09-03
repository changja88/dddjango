from __future__ import annotations

import typing
from typing import Any, Optional
from typing import Any as _Any


def take_bare(x: Any) -> None:
    return None


def give_bare() -> Any:
    return None


def take_optional(x: Optional[Any]) -> None:
    return None


def take_alias(x: _Any) -> None:
    return None


def take_attribute(x: typing.Any) -> None:
    return None


def take_star(**kwargs: Any) -> None:
    return None


def take_pipe_none(x: Any | None) -> None:
    return None


def take_string(x: "Any") -> None:
    return None


def hold_nested() -> None:
    y: dict[str, Any] = {}
    return None
