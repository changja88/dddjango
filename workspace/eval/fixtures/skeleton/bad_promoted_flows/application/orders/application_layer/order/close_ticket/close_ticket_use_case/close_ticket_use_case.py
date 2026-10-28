from __future__ import annotations

from typing import Callable

from application.orders.application_layer.order.close_ticket.close_ticket_command import CloseTicketCommand
from application.orders.application_layer.order.close_ticket.close_ticket_result import CloseTicketResult
from application.orders.application_layer.port.unit_of_work.order_unit_of_work import OrderUnitOfWork

from .close_ticket_frame import CloseTicketFrame
from .ticket_reply import TicketReply


class CloseTicketUseCase:
    def __init__(self, new_unit_of_work: Callable[[], OrderUnitOfWork]) -> None:
        self._frame: CloseTicketFrame = CloseTicketFrame(new_unit_of_work)
        self._ticket_reply: TicketReply = TicketReply(self, frame=self._frame)

    def reopen_ticket(self, ticket_id: int) -> None:
        self._frame.record_done(ticket_id)

    def execute(self, command: CloseTicketCommand) -> CloseTicketResult:
        self._ticket_reply.reply(command.target_id)
        return CloseTicketResult(target_id=command.target_id, done=True)
