from enum import Enum

from ninja import Schema


class BillingErrorCode(str, Enum):
    INVOICE_NOT_FOUND = "invoice_not_found"


class PaymentErrorSchema(Schema):
    code: str
    message: str
