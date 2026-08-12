from application.orders.application_layer.port.payment_gateway.payment_gateway_port import (
    PaymentGatewayPort,
)
from application.orders.domain_layer.order.order import Order

_KIND: str = Order.__name__ + PaymentGatewayPort.__name__
