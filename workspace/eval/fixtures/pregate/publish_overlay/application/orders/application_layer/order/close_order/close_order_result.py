from dataclasses import dataclass


@dataclass(frozen=True)
class CloseOrderResult:
    order_id: int
