from __future__ import annotations

from collections.abc import Callable

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository

from .card_settlement import CardSettlement
from .settle_order_frame import SettleOrderFrame


class SettleOrderUseCase:
    def __init__(self, order_repository: OrderRepository, new_unit_of_work: Callable[[], OrdersUnitOfWork]) -> None:
        self._new_unit_of_work: Callable[[], OrdersUnitOfWork] = new_unit_of_work
        self._frame: SettleOrderFrame = SettleOrderFrame(order_repository)
        self._card_settlement: CardSettlement = CardSettlement(self._frame)

    def execute(self, order_id: str, amount: int) -> bool:
        with self._new_unit_of_work():
            order: Order = self._card_settlement.prepare(order_id, amount)
            self._frame.save_order(order)
            self._card_settlement.finish(order)
        return True
