from dataclasses import dataclass


@dataclass(frozen=True)
class MoveSeatResult:
    target_id: int
    done: bool
