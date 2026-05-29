from dataclasses import dataclass


@dataclass(frozen=True)
class ReserveProductStockCommand:
    product_id: int
    quantity: int

