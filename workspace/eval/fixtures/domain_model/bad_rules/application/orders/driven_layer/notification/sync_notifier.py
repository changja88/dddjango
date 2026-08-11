from __future__ import annotations

from application.orders.domain_layer.order.event.order_synced import OrderSynced


def notify(event: OrderSynced) -> None:
    return None
