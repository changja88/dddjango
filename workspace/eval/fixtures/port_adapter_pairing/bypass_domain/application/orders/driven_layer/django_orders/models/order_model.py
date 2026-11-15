from typing import Final

from django.db import models

from application.orders.domain_layer.order.value_object.order_status import OrderStatus
from application.orders.domain_layer.order.value_object.refund_plan import RefundPlan, RefundRule

PENDING_VALUE: Final[str] = OrderStatus.PENDING.value
STANDARD_RULE: Final[RefundRule] = RefundPlan.STANDARD.value
BARE_PENDING: Final = OrderStatus.PENDING.value
Kind = OrderStatus


class OrderModel(models.Model):
    STATUS_PENDING: Final[str] = OrderStatus.PENDING.value
    STATUS_SHIPPED: "Final[str]" = OrderStatus.SHIPPED.value
    STATUS_PLAIN: str = OrderStatus.PENDING.value
    STANDARD_REFUND: Final[RefundRule] = RefundPlan.STANDARD.value
    Status: type[OrderStatus] = OrderStatus

    status: models.CharField = models.CharField(
        max_length=20, choices=[(s.value, s.name.title()) for s in OrderStatus], default=OrderStatus.PENDING.value
    )
