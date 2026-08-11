from application.orders.application_layer.port.invoice_lookup.exception import InvoiceLookupFailed


class BillingInvoiceLookupAdapter:
    def fetch(self, invoice_id: str):
        try:
            return self._call(invoice_id)
        except Exception as exc:
            raise InvoiceLookupFailed(str(exc))

    def _call(self, invoice_id: str):
        return None
