from dataclasses import dataclass


@dataclass(frozen=True)
class HoldStockResult:
    target_id: int
    done: bool
