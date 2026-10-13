from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ArchivedEvents:
    reservation_id: str
