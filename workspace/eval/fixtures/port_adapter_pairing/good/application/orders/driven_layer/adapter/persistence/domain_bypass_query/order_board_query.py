from __future__ import annotations

from application.orders.application_layer.port.domain_bypass_query.order_board.order_board_query import OrderBoardDomainBypassQuery


class DjangoOrderBoardDomainBypassQuery(OrderBoardDomainBypassQuery):
    def fetch_rows(self) -> list:
        return []
