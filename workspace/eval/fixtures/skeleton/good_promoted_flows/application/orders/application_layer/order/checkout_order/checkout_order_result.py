from dataclasses import dataclass


@dataclass(frozen=True)
class CheckoutOrderResult:
    target_id: int
    done: bool
