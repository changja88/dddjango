from __future__ import annotations

from .parcel_weight import ParcelWeight
from .ship_parcel_frame import ShipParcelFrame


class ParcelLabel:
    def __init__(self, frame: ShipParcelFrame, parcel_weight: ParcelWeight) -> None:
        self._frame: ShipParcelFrame = frame
        self._parcel_weight: ParcelWeight = parcel_weight

    def attach(self, parcel_id: int) -> None:
        if self._parcel_weight.weigh(parcel_id) > 0:
            self._frame.record_done(parcel_id)
