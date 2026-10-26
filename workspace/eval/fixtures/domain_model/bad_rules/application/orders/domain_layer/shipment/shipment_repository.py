from __future__ import annotations

from abc import ABC, abstractmethod

from application.orders.domain_layer.shipment.shipment import Shipment


class ShipmentRepository(ABC):
    @abstractmethod
    def get(self, shipment_id: str) -> Shipment: ...

    @abstractmethod
    def save(self, shipment: Shipment) -> None: ...
