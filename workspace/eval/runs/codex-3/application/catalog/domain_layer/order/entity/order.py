from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Order:
    product_id: int
    quantity: int
    unit_price: int
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        if type(self.product_id) is not int or self.product_id <= 0:
            raise ValueError("product_id must be a positive integer.")
        if type(self.quantity) is not int or self.quantity <= 0:
            raise ValueError("quantity must be a positive integer.")
        if type(self.unit_price) is not int or self.unit_price < 0:
            raise ValueError("unit_price must be a non-negative integer.")
