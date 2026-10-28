from dataclasses import dataclass


@dataclass(frozen=True)
class PackBoxQuery:
    target_id: int
