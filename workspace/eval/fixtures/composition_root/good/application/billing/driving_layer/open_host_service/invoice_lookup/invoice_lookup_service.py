from .contract.request.get_invoice_request import GetInvoiceRequest
from .contract.response.get_invoice_response import GetInvoiceResponse
from .contract.exception.invoice_unavailable import InvoiceUnavailable


def get_invoice_query(request: GetInvoiceRequest) -> GetInvoiceResponse:
    if not request.invoice_id:
        raise InvoiceUnavailable()
    return GetInvoiceResponse(code="OK", invoice_id=request.invoice_id)
