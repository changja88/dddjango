from application.billing.driving_layer.open_host_service.invoice_lookup.invoice_lookup_service import get_invoice_query
from application.orders.driven_layer.django_orders.models.order_model import OrderModel


class InvoiceFetcher:
    def fetch(self) -> str:
        try:
            return get_invoice_query()
        except ValueError:
            return ""
