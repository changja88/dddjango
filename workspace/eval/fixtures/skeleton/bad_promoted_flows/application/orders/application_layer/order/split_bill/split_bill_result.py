from dataclasses import dataclass


@dataclass(frozen=True)
class SplitBillResult:
    target_id: int
    done: bool
