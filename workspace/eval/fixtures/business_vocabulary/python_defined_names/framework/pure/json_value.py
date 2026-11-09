from __future__ import annotations

from collections.abc import Mapping, Sequence

type JsonScalar = bool | int | float | str | None
type JsonValue = JsonScalar | Sequence[JsonValue] | Mapping[str, JsonValue]
