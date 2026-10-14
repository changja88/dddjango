from dataclasses import dataclass


@dataclass(frozen=True)
class ArchiveOrderCommand:
    order_id: int
    note: str
