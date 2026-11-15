from application.orders.domain_layer.order.value_object.order_status import OrderStatus

OPEN: tuple[str, ...] = (OrderStatus.PENDING.value,)
