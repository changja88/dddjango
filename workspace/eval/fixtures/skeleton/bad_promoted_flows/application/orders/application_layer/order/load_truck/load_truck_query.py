from dataclasses import dataclass


@dataclass(frozen=True)
class LoadTruckQuery:
    target_id: int
