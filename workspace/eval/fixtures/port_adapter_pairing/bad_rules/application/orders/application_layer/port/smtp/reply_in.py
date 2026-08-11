from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReplyIn:
    accepted: bool
    reason: str
