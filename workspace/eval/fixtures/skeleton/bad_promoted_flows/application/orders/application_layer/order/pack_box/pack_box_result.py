from dataclasses import dataclass


@dataclass(frozen=True)
class PackBoxResult:
    target_id: int
    done: bool
