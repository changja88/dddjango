from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ArchivedObject:
    reservation_id: str
