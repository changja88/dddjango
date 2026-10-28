from __future__ import annotations

from typing import Protocol

from .close_ticket_frame import CloseTicketFrame


class _TicketOwner(Protocol):
    def reopen_ticket(self, ticket_id: int) -> None: ...


class TicketReply:
    def __init__(self, owner: _TicketOwner, frame: CloseTicketFrame) -> None:
        self._owner: _TicketOwner = owner
        self._frame: CloseTicketFrame = frame

    def reply(self, ticket_id: int) -> None:
        self._owner.reopen_ticket(ticket_id)
        self._frame.record_done(ticket_id)
