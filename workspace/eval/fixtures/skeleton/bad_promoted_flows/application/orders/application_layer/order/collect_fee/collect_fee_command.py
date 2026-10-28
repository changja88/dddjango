from dataclasses import dataclass


@dataclass(frozen=True)
class CollectFeeCommand:
    target_id: int
