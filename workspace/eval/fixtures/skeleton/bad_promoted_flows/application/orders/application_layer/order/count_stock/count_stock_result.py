from dataclasses import dataclass


@dataclass(frozen=True)
class CountStockResult:
    target_id: int
    done: bool
