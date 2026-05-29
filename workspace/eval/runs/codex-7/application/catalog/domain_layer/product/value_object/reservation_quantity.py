from dataclasses import dataclass

from application.catalog.domain_layer.product.exception import (
    InvalidReservationQuantity,
)


@dataclass(frozen=True)
class ReservationQuantity:
    value: int

    def __post_init__(self) -> None:
        if type(self.value) is not int or self.value < 1:
            raise InvalidReservationQuantity(self.value)

