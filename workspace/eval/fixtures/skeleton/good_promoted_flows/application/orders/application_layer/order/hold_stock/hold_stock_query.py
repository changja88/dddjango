from dataclasses import dataclass


@dataclass(frozen=True)
class HoldStockQuery:
    target_id: int
