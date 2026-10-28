from dataclasses import dataclass


@dataclass(frozen=True)
class PayInvoiceResult:
    target_id: int
    done: bool
