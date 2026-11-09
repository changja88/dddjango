def wire_shipping_events() -> None:
    from application.shipping.driving_layer.event_subscription.event_router import ROUTES
    from application.shipping.driving_layer.event_subscription.parcel_sent_subscription import parcel_sent_subscription

    print(ROUTES, parcel_sent_subscription)
