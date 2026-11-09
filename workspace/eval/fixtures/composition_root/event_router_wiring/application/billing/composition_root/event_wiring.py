from application.billing.driving_layer.event_subscription import event_router, invoice_paid_subscription
from framework.broker.internal.internal_broker import internal_broker


def wire_billing_events() -> None:
    internal_broker.subscribe(event_router.ROUTES, invoice_paid_subscription)
