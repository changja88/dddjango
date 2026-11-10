from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NoteOrderResult:
    order_id: str


@dataclass(frozen=True)
class NoteOrderError:
    reason: str


@dataclass(frozen=True)
class NoteTooLongError(NoteOrderError):
    limit: int
