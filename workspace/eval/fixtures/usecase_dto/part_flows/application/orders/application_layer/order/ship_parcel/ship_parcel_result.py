from dataclasses import dataclass


@dataclass(frozen=True)
class ShipParcelResult:
    order_id: str
