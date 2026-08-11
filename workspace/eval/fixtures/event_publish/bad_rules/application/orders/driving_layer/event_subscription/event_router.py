from __future__ import annotations

from application.orders.driving_layer.event_subscription.billing_settled_subscription import on_billing_settled

ROUTES = {"billing_settled": on_billing_settled}

print("wired")
