from dataclasses import dataclass


@dataclass(frozen=True)
class CountStockCommand:
    target_id: int
