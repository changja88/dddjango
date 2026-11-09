from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Final

from framework.pure.json_value import JsonValue

_NUL: Final[str] = "\x00"


def strip_nul(value: JsonValue) -> JsonValue:
    if isinstance(value, str):
        return value.replace(_NUL, "")
    if isinstance(value, Mapping):
        return {key.replace(_NUL, ""): strip_nul(item) for key, item in value.items()}
    if isinstance(value, Sequence):
        return [strip_nul(item) for item in value]
    return value
