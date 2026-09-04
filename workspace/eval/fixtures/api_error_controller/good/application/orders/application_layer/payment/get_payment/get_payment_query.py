from dataclasses import dataclass


@dataclass(frozen=True)
class GetPaymentQuery:
    payment_id: str
