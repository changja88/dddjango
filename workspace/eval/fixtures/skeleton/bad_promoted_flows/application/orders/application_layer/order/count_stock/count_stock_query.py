from dataclasses import dataclass


@dataclass(frozen=True)
class CountStockQuery:
    target_id: int
