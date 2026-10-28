from dataclasses import dataclass


@dataclass(frozen=True)
class CollectFeeQuery:
    target_id: int
