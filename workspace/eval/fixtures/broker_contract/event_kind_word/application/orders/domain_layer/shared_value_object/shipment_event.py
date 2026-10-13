from __future__ import annotations

from typing import TypeAlias

from application.orders.domain_layer.shared_value_object.shipment_completed import ShipmentCompleted
from application.orders.domain_layer.shared_value_object.shipment_started import ShipmentStarted

ShipmentEvent: TypeAlias = ShipmentStarted | ShipmentCompleted
