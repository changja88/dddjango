from dataclasses import dataclass


@dataclass(frozen=True)
class SplitBillQuery:
    target_id: int
