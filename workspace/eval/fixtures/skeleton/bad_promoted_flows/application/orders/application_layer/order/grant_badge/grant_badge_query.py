from dataclasses import dataclass


@dataclass(frozen=True)
class GrantBadgeQuery:
    target_id: int
