from __future__ import annotations

from typing import Callable

from application.orders.application_layer.order.cancel_trip.cancel_trip_command import CancelTripCommand
from application.orders.application_layer.order.cancel_trip.cancel_trip_result import CancelTripResult
from application.orders.application_layer.port.unit_of_work.order_unit_of_work import OrderUnitOfWork

from .cancel_trip_frame import CancelTripFrame
from .trip_refund import TripRefund


class CancelTripUseCase:
    def __init__(self, new_unit_of_work: Callable[[], OrderUnitOfWork]) -> None:
        self._frame: CancelTripFrame = CancelTripFrame(new_unit_of_work)
        self._trip_refund: TripRefund = TripRefund(frame=self._frame)

    def _retry_cancel(self, target_id: int) -> None:
        self._frame.record_done(target_id)

    def execute(self, command: CancelTripCommand) -> CancelTripResult:
        self._trip_refund.run(command.target_id, on_retry=self._retry_cancel)
        return CancelTripResult(target_id=command.target_id, done=True)
