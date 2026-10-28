from __future__ import annotations

from .ship_parcel_frame import ShipParcelFrame


class ParcelWeight:
    def __init__(self, frame: ShipParcelFrame) -> None:
        self._frame: ShipParcelFrame = frame

    def weigh(self, parcel_id: int) -> int:
        self._frame.record_done(parcel_id)
        return parcel_id * 2
