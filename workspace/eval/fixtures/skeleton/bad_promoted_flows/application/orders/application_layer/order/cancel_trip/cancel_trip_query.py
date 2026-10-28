from dataclasses import dataclass


@dataclass(frozen=True)
class CancelTripQuery:
    target_id: int
