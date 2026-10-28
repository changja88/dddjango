from __future__ import annotations

from collections.abc import Callable

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork

from .ship_order_frame import ShipOrderFrame


class ParcelPacking:
    def __init__(self, frame: ShipOrderFrame, new_unit_of_work: Callable[[], OrdersUnitOfWork]) -> None:
        self._frame: ShipOrderFrame = frame
        self._new_unit_of_work: Callable[[], OrdersUnitOfWork] = new_unit_of_work

    def run(self, order_id: str) -> bool:
        with self._new_unit_of_work():
            return self._frame.commit_order_change(order_id, lambda current: current.ship())
