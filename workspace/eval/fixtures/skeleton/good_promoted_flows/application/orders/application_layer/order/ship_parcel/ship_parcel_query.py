from dataclasses import dataclass


@dataclass(frozen=True)
class ShipParcelQuery:
    target_id: int
