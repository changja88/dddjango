from dataclasses import dataclass


@dataclass(frozen=True)
class ShipParcelResult:
    target_id: int
    done: bool
