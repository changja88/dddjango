from dataclasses import dataclass


@dataclass(frozen=True)
class LoadTruckCommand:
    target_id: int
