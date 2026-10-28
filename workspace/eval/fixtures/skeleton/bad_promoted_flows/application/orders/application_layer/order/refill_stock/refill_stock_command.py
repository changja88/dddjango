from dataclasses import dataclass


@dataclass(frozen=True)
class RefillStockCommand:
    target_id: int
