from dataclasses import dataclass


@dataclass(frozen=True)
class ShipParcelCommand:
    order_id: str
