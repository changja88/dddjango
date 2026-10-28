from dataclasses import dataclass


@dataclass(frozen=True)
class MergeCartCommand:
    target_id: int
