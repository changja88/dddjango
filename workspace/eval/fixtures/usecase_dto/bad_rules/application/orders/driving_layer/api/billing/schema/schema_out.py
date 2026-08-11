from application.orders.domain_layer.order.entity.line import Line
from application.orders.driven_layer.django_orders.models.order_model import OrderModel


class BillingOut:
    line: Line
