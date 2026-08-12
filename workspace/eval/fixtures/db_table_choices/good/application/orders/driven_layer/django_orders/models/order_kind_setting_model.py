from django.db import models

from application.orders.domain_layer.order.value_object.order_kind import OrderKind


class OrderKindSettingModel(models.Model):
    kind = models.CharField(
        max_length=32,
        choices=[(member.value, member.value) for member in OrderKind],
    )

    class Meta:
        db_table = "orders_order_kind_setting"
