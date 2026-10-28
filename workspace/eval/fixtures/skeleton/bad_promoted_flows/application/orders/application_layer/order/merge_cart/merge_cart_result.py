from dataclasses import dataclass


@dataclass(frozen=True)
class MergeCartResult:
    target_id: int
    done: bool
