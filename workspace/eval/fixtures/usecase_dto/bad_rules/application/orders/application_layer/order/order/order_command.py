from application.orders.driving_layer.api.order.schema.schema_in import PlaceOrderIn
from application.orders.domain_layer.order.entity.line import Line
from application.orders.domain_layer.order.order import Order


class OrderCommand:
    line: Line
