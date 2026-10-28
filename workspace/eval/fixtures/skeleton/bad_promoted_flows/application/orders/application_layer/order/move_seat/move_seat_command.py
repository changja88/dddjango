from dataclasses import dataclass


@dataclass(frozen=True)
class MoveSeatCommand:
    target_id: int
