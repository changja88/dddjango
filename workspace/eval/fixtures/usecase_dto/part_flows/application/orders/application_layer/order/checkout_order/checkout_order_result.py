from dataclasses import dataclass


@dataclass(frozen=True)
class CheckoutOrderResult:
    order_id: str
