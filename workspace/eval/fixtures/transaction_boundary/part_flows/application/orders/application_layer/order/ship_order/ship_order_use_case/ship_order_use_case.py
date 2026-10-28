from __future__ import annotations

from collections.abc import Callable

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order_repository import OrderRepository

from .parcel_packing import ParcelPacking
from .ship_order_frame import ShipOrderFrame


class ShipOrderUseCase:
    def __init__(self, order_repository: OrderRepository, new_unit_of_work: Callable[[], OrdersUnitOfWork]) -> None:
        self._frame: ShipOrderFrame = ShipOrderFrame(order_repository, new_unit_of_work)
        self._parcel_packing: ParcelPacking = ParcelPacking(self._frame, new_unit_of_work)

    def execute(self, order_id: str) -> bool:
        return self._parcel_packing.run(order_id)
