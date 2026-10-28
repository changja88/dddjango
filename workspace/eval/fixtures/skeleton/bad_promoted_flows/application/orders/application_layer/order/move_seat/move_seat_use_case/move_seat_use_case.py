from __future__ import annotations

from typing import Callable

from application.orders.application_layer.order.move_seat.move_seat_command import MoveSeatCommand
from application.orders.application_layer.order.move_seat.move_seat_result import MoveSeatResult
from application.orders.application_layer.port.unit_of_work.order_unit_of_work import OrderUnitOfWork

from .move_seat_frame import MoveSeatFrame
from .seat_move import SeatMove


class MoveSeatUseCase:
    def __init__(self, new_unit_of_work: Callable[[], OrderUnitOfWork]) -> None:
        self._frame: MoveSeatFrame = MoveSeatFrame(new_unit_of_work)
        self._seat_move: SeatMove = SeatMove(frame=self._frame)

    def _retry_move(self, target_id: int) -> None:
        self._frame.record_done(target_id)

    def execute(self, command: MoveSeatCommand) -> MoveSeatResult:
        seat_id: int = command.target_id

        def retry() -> None:
            self._retry_move(seat_id)

        self._seat_move.run(seat_id, on_retry=retry)
        return MoveSeatResult(target_id=command.target_id, done=True)
