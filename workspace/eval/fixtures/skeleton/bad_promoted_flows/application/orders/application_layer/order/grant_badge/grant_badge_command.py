from dataclasses import dataclass


@dataclass(frozen=True)
class GrantBadgeCommand:
    target_id: int
