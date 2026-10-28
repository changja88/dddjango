from dataclasses import dataclass


@dataclass(frozen=True)
class LoadTruckResult:
    target_id: int
    done: bool
