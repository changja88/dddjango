from dataclasses import dataclass


@dataclass(frozen=True)
class CollectFeeResult:
    target_id: int
    done: bool
