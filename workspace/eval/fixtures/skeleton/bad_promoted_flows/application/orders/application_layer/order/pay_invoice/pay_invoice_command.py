from dataclasses import dataclass


@dataclass(frozen=True)
class PayInvoiceCommand:
    target_id: int
