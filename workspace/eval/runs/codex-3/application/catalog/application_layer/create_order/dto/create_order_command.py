from dataclasses import dataclass


@dataclass(frozen=True)
class CreateOrderCommand:
    product_id: int
    quantity: int

    def __post_init__(self) -> None:
        if type(self.product_id) is not int or self.product_id <= 0:
            raise ValueError("product_id must be a positive integer.")
        if type(self.quantity) is not int or self.quantity <= 0:
            raise ValueError("quantity must be a positive integer.")
