from dataclasses import dataclass


@dataclass(frozen=True)
class ReturnItemResult:
    target_id: int
    done: bool
