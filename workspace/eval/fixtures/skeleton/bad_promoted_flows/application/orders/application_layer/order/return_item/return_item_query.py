from dataclasses import dataclass


@dataclass(frozen=True)
class ReturnItemQuery:
    target_id: int
