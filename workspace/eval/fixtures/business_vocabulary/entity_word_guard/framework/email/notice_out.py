from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NoticeOut:
    code: str
    quantity: int
    event_id: str
