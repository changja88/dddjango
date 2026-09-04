from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any, TypeIs


class LeakyHolder:
    payload: Mapping[str, object]


def leak_return(raw: str) -> dict[str, object]:
    return {"raw": raw}


def leak_param(rows: list[dict[str, Any]]) -> None:
    return None


def is_record(value: object) -> TypeIs[dict[str, Any]]:
    return isinstance(value, dict)


def parse_unchecked(raw: str) -> None:
    payload: dict[str, Any] = json.loads(raw)
    return None
