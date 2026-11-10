from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NoteOrderCommand:
    order_id: str
