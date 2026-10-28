from dataclasses import dataclass


@dataclass(frozen=True)
class PayInvoiceQuery:
    target_id: int
