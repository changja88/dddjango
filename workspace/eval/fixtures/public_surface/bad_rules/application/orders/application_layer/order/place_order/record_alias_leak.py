from typing import TypeAlias

Payload: TypeAlias = dict[str, object]
type Snapshot = dict[str, object]


def payload_of(raw: str) -> Payload:
    return {"raw": raw}


def snapshot_of(raw: str) -> Snapshot:
    return {"raw": raw}
