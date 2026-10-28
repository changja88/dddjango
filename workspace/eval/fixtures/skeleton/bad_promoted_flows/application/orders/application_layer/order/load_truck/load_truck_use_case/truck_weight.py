from __future__ import annotations

from .load_truck_frame import LoadTruckFrame


class TruckWeight:
    def __init__(self, frame: LoadTruckFrame) -> None:
        self._frame: LoadTruckFrame = frame

    def weigh(self, truck_id: int) -> None:
        self._frame.record_load(truck_id, self)
