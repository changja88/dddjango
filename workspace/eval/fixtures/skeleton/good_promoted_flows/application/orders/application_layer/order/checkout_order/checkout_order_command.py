from dataclasses import dataclass


@dataclass(frozen=True)
class CheckoutOrderCommand:
    target_id: int
    requested_route: str
