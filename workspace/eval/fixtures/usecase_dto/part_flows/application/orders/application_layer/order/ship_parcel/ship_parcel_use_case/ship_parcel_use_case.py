"""②′ 폴더 본체 — `__init__` 이 틀 → 단계 차례로 부품을 만든다."""
from __future__ import annotations

from application.orders.application_layer.order.ship_parcel.ship_parcel_command import ShipParcelCommand
from application.orders.application_layer.order.ship_parcel.ship_parcel_result import ShipParcelResult
from application.orders.application_layer.port.event_publisher.event_publisher_port import EventPublisherPort
from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order_repository import OrderRepository

from .parcel_dispatch import ParcelDispatch
from .ship_parcel_frame import ShipParcelFrame


class ShipParcelUseCase:
    def __init__(self, order_repository: OrderRepository, unit_of_work: OrdersUnitOfWork,
                 event_publisher: EventPublisherPort) -> None:
        self._frame: ShipParcelFrame = ShipParcelFrame(order_repository, unit_of_work, event_publisher)
        self._parcel_dispatch: ParcelDispatch = ParcelDispatch(frame=self._frame)

    def execute(self, command: ShipParcelCommand) -> ShipParcelResult:
        self._parcel_dispatch.dispatch(command.order_id)
        return ShipParcelResult(order_id=command.order_id)
