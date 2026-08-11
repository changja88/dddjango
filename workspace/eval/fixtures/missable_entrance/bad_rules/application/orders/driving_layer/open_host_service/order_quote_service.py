from __future__ import annotations

from application.orders.driving_layer.open_host_service.contract.exception.quote_unavailable import QuoteUnavailable


def order_quote_service(order_id: str) -> str:
    if order_id == "":
        raise QuoteUnavailable()
    return "quote"
