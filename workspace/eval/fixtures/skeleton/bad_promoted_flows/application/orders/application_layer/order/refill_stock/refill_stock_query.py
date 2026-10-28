from dataclasses import dataclass


@dataclass(frozen=True)
class RefillStockQuery:
    target_id: int
