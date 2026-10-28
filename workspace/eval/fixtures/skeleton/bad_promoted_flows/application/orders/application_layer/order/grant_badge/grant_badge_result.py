from dataclasses import dataclass


@dataclass(frozen=True)
class GrantBadgeResult:
    target_id: int
    done: bool
