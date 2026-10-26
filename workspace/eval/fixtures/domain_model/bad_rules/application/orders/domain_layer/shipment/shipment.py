from __future__ import annotations


class Shipment:
    def __init__(self, shipment_id: str) -> None:
        self.shipment_id: str = shipment_id
        self.parcels: list = []

    def load(self, parcel_id: str) -> None:
        self.parcels.append(parcel_id)
        self._ensure_valid()

    def _ensure_valid(self) -> None:
        return None
