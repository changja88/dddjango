from dataclasses import dataclass


@dataclass(frozen=True)
class PackBoxCommand:
    target_id: int
