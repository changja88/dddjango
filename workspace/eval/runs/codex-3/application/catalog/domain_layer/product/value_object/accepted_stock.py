from dataclasses import dataclass


@dataclass(frozen=True)
class AcceptedStock:
    product_id: int
    accepted_quantity: int
    unit_price: int

    def __post_init__(self) -> None:
        if type(self.product_id) is not int or self.product_id <= 0:
            raise ValueError("product_id must be a positive integer.")
        if type(self.accepted_quantity) is not int or self.accepted_quantity <= 0:
            raise ValueError("accepted_quantity must be a positive integer.")
        if type(self.unit_price) is not int or self.unit_price < 0:
            raise ValueError("unit_price must be a non-negative integer.")
