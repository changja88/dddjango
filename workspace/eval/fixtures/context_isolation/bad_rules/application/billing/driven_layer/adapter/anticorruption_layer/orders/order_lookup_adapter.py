from application.orders.driving_layer.open_host_service.order_lookup.order_lookup_service import fetch_order


class OrdersOrderLookupAdapter:
    def fetch(self) -> str:
        return fetch_order("1", True)
