"""기존 ② 폴더 본체 — 실패 타입 부품을 형제에서 가져올 뿐 부품을 만들지 않는다(②′ 폴더 아님)."""
from __future__ import annotations

from application.orders.application_layer.order.place_order.place_order_command import PlaceOrderCommand
from application.orders.application_layer.order.place_order.place_order_result import PlaceOrderResult
from application.orders.domain_layer.order.order_repository import OrderRepository

from .order_rejection import OrderRejection


class PlaceOrderUseCase:
    def __init__(self, order_repository: OrderRepository) -> None:
        self._order_repository: OrderRepository = order_repository

    def execute(self, command: PlaceOrderCommand) -> PlaceOrderResult:
        try:
            order = self._order_repository.get(command.order_id)
        except LookupError as exc:
            raise OrderRejection(command.order_id) from exc
        self._order_repository.save(order)
        return PlaceOrderResult(order_id=command.order_id)
