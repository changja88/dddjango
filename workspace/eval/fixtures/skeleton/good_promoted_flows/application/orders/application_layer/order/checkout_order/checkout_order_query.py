from dataclasses import dataclass


@dataclass(frozen=True)
class CheckoutOrderQuery:
    target_id: int
