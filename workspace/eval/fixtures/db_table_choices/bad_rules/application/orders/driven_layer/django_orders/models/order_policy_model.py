from django.db import models

from application.orders.domain_layer.order.value_object.order_kind import OrderKind


class OrderPolicyModel(models.Model):
    kind = models.CharField(max_length=32)

    class Meta:
        db_table = "orders_order_policy"

    def normalized_kind(self) -> str:
        return OrderKind.resolve(self.kind).value
