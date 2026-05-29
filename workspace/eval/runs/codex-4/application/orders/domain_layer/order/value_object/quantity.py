from dataclasses import dataclass

from application.orders.domain_layer.order.exception import InvalidQuantity


@dataclass(frozen=True)
class Quantity:
    value: int

    def __post_init__(self) -> None:
        if type(self.value) is not int or self.value <= 0:
            raise InvalidQuantity("quantity must be a positive integer")
