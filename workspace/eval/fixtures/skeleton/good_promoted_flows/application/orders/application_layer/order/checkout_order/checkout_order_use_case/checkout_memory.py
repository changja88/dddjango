from dataclasses import dataclass


@dataclass
class _CheckoutMemory:
    order_id: int
    paid: bool = False
