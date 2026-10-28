from dataclasses import dataclass


@dataclass(frozen=True)
class CancelTripResult:
    target_id: int
    done: bool
