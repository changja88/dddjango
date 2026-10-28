from dataclasses import dataclass


@dataclass(frozen=True)
class ReturnItemCommand:
    target_id: int
