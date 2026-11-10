from __future__ import annotations

from application.orders.application_layer.order.frame_move.frame_move_use_case.frame_move_frame import FrameMoveFrame
from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order_repository import OrderRepository


class FrameMoveUseCase:
    def __init__(self, order_repository: OrderRepository, unit_of_work: OrdersUnitOfWork) -> None:
        self._frame: FrameMoveFrame = FrameMoveFrame(order_repository, unit_of_work)

    def execute(self, order_id: str, other_id: str) -> None:
        self._frame.move(order_id, other_id)
