from dataclasses import dataclass


@dataclass(frozen=True)
class CheckoutOrderCommand:
    order_id: str
    sku: str
    line: str
