from __future__ import annotations

from application.billing.application_layer.billing.record_order.record_order_use_case import RecordOrderUseCase
from application.billing.published_event.billing_settled import BillingSettled
from application.orders.composition_root.dependency_wiring import build_record_settlement


def on_billing_settled(event: BillingSettled) -> None:
    use_case = build_record_settlement()
    if event.amount > 0:
        use_case.execute(event.order_id)
