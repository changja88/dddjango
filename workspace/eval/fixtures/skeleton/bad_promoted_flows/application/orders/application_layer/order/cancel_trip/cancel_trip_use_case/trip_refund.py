from __future__ import annotations

from typing import Callable

from .cancel_trip_frame import CancelTripFrame


class TripRefund:
    def __init__(self, frame: CancelTripFrame) -> None:
        self._frame: CancelTripFrame = frame

    def run(self, target_id: int, on_retry: Callable[[], None]) -> None:
        self._frame.record_done(target_id)
        on_retry()
