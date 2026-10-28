from dataclasses import dataclass


@dataclass(frozen=True)
class ShipParcelCommand:
    target_id: int
