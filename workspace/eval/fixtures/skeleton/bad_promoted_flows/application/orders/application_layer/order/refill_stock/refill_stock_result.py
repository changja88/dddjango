from dataclasses import dataclass


@dataclass(frozen=True)
class RefillStockResult:
    target_id: int
    done: bool
