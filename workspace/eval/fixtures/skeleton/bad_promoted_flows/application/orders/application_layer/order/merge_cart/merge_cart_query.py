from dataclasses import dataclass


@dataclass(frozen=True)
class MergeCartQuery:
    target_id: int
