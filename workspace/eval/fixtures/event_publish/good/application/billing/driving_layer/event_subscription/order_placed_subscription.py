from __future__ import annotations

from application.billing.composition_root.dependency_wiring import build_record_order
from application.orders.published_event.order_placed import OrderPlaced


def on_order_placed(event: OrderPlaced) -> None:
    use_case = build_record_order()
    use_case.execute(event.order_id)
