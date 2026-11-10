from __future__ import annotations

from application.orders.driving_layer.open_host_service.order_desk.contract.exception.order_desk_published_error import OrderDeskPublishedError


class OrderUnavailableException(OrderDeskPublishedError):
    def __init__(self, category: str) -> None:
        super().__init__(category)
        self.category: str = category
