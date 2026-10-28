from __future__ import annotations

from typing import Callable

from application.orders.application_layer.order.load_truck.load_truck_command import LoadTruckCommand
from application.orders.application_layer.order.load_truck.load_truck_result import LoadTruckResult
from application.orders.application_layer.port.unit_of_work.order_unit_of_work import OrderUnitOfWork

from .load_truck_frame import LoadTruckFrame
from .truck_weight import TruckWeight


class LoadTruckUseCase:
    def __init__(self, new_unit_of_work: Callable[[], OrderUnitOfWork]) -> None:
        self._frame: LoadTruckFrame = LoadTruckFrame(new_unit_of_work)
        self._truck_weight: TruckWeight = TruckWeight(frame=self._frame)

    def execute(self, command: LoadTruckCommand) -> LoadTruckResult:
        self._truck_weight.weigh(command.target_id)
        return LoadTruckResult(target_id=command.target_id, done=True)
