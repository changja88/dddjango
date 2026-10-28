from __future__ import annotations

from typing import Callable

from .move_seat_frame import MoveSeatFrame


class SeatMove:
    def __init__(self, frame: MoveSeatFrame) -> None:
        self._frame: MoveSeatFrame = frame

    def run(self, target_id: int, on_retry: Callable[[], None]) -> None:
        self._frame.record_done(target_id)
        on_retry()
