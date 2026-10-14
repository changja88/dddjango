from dataclasses import dataclass


@dataclass(frozen=True)
class RenameOrderResult:
    order_id: int
