from application.orders.driving_layer.open_host_service.order_lookup.order_lookup_service import get_order_query
from application.orders.driving_layer.open_host_service.order_lookup.contract.exception.order_lookup_published_error import OrderLookupPublishedError
from application.billing.application_layer.port.order_lookup.order_lookup_port import OrderLookupPort


class OrdersOrderLookupAdapter(OrderLookupPort):
    def fetch(self, order_id: str) -> str:
        try:
            return get_order_query(order_id)
        except OrderLookupPublishedError:
            return ""
