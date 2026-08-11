from __future__ import annotations

from application.orders.application_layer.port.domain_bypass_query.board.board_query import BoardDomainBypassQuery
from application.orders.application_layer.port.smtp.reply_in import ReplyIn


class PlaceOrderUseCase:
    def execute(self, board: BoardDomainBypassQuery, exc: object) -> None:
        rows = board.fetch()
        if rows:
            reply = ReplyIn(accepted=True, reason="full")
        if exc.status_code == 429:
            return None
