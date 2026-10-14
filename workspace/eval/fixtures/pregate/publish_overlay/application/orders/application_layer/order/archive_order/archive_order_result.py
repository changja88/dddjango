from dataclasses import dataclass


@dataclass(frozen=True)
class ArchiveOrderResult:
    order_id: int
