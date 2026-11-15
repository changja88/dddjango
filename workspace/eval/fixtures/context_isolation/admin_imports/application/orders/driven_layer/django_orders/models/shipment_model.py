from django.db import models

from application.orders.domain_layer.order.value_object.order_status import OrderStatus


class ShipmentModel(models.Model):
    Status: type[OrderStatus] = OrderStatus
