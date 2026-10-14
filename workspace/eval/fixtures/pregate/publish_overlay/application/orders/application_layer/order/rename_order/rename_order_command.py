from dataclasses import dataclass


@dataclass(frozen=True)
class RenameOrderCommand:
    order_id: int
    note: str
