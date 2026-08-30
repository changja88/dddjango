# 타 BC(billing)의 open_host_service 소비 — #13·#473 이 요구하는 표준 소비이며 경로에 `driving_layer` 가
# 끼어 있어도 #101(자기 BC driving 금지)의 대상이 아니다(스펙 #101 2026-08-31 부칙 회귀 케이스).
from application.billing.driving_layer.open_host_service.invoice_lookup.invoice_lookup_service import get_invoice_query
from application.billing.driving_layer.open_host_service.invoice_lookup.contract.request.get_invoice_request import GetInvoiceRequest
from application.billing.driving_layer.open_host_service.invoice_lookup.contract.exception.invoice_lookup_published_error import InvoiceLookupPublishedError
from application.orders.application_layer.port.invoice_lookup.invoice_lookup_port import InvoiceLookupPort


class BillingInvoiceLookupAdapter(InvoiceLookupPort):
    def fetch(self, invoice_id: str) -> str:
        try:
            return get_invoice_query(GetInvoiceRequest(invoice_id=invoice_id)).invoice_id
        except InvoiceLookupPublishedError:
            return ""
