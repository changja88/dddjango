from dataclasses import dataclass


@dataclass(frozen=True)
class HoldStockCommand:
    target_id: int
