from dataclasses import dataclass


@dataclass(frozen=True)
class SplitBillCommand:
    target_id: int
