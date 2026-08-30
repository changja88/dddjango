from dataclasses import dataclass


@dataclass(frozen=True)
class GetInvoiceResponse:
    code: str
    invoice_id: str
