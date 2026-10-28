from __future__ import annotations

from typing import Callable

from application.orders.application_layer.order.book_room.book_room_command import BookRoomCommand
from application.orders.application_layer.order.book_room.book_room_result import BookRoomResult
from application.orders.application_layer.port.unit_of_work.order_unit_of_work import OrderUnitOfWork

from .book_room_frame import BookRoomFrame
from .room_hold import RoomHold


class BookRoomUseCase:
    def __init__(self, new_unit_of_work: Callable[[], OrderUnitOfWork]) -> None:
        self._frame: BookRoomFrame = BookRoomFrame(new_unit_of_work)
        self._room_hold: RoomHold = RoomHold(self._frame)

    def execute(self, command: BookRoomCommand) -> BookRoomResult:
        self._room_hold.run(command.target_id, frame=self._frame)
        return BookRoomResult(target_id=command.target_id, done=True)
