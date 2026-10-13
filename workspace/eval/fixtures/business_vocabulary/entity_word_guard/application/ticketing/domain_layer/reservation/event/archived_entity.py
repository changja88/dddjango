from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ArchivedEntity:
    reservation_id: str
