def wire() -> object:
    from application.orders.driving_layer.event_subscription.order_paid_subscription import on_order_paid

    return on_order_paid
