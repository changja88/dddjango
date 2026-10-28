from dataclasses import dataclass


@dataclass(frozen=True)
class CancelTripCommand:
    target_id: int
