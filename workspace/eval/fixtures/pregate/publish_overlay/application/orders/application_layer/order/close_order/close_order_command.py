from dataclasses import dataclass


@dataclass(frozen=True)
class CloseOrderCommand:
    order_id: int
    note: str
