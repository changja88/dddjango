from django.db import models

from application.orders.domain_layer.order.order import Order

_AGGREGATE_NAME: str = Order.__name__


class OrderAuditModel(models.Model):
    note = models.CharField(max_length=64)

    class Meta:
        db_table = "orders_order_audit"
