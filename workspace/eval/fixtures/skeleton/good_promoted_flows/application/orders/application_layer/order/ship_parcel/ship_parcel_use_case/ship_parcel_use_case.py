from __future__ import annotations

from typing import Callable

from application.orders.application_layer.order.ship_parcel.ship_parcel_command import ShipParcelCommand
from application.orders.application_layer.order.ship_parcel.ship_parcel_result import ShipParcelResult
from application.orders.application_layer.port.unit_of_work.order_unit_of_work import OrderUnitOfWork

from .parcel_label import ParcelLabel
from .parcel_weight import ParcelWeight
from .ship_parcel_frame import ShipParcelFrame


class ShipParcelUseCase:
    def __init__(self, new_unit_of_work: Callable[[], OrderUnitOfWork]) -> None:
        self._frame: ShipParcelFrame = ShipParcelFrame(new_unit_of_work)
        self._parcel_weight: ParcelWeight = ParcelWeight(frame=self._frame)
        self._parcel_label: ParcelLabel = ParcelLabel(frame=self._frame, parcel_weight=self._parcel_weight)

    def execute(self, command: ShipParcelCommand) -> ShipParcelResult:
        self._parcel_label.attach(command.target_id)
        return ShipParcelResult(target_id=command.target_id, done=True)
