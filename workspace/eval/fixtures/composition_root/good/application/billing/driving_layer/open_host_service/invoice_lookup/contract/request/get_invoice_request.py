from dataclasses import dataclass


@dataclass(frozen=True)
class GetInvoiceRequest:
    invoice_id: str
