from dataclasses import dataclass


@dataclass(frozen=True)
class MoveSeatQuery:
    target_id: int
