from typing import Final

from django.db import models

from application.orders.domain_layer.order.value_object.order_status import *  # noqa: F403


class StarSeedModel(models.Model):
    Status = OrderStatus
    STATUS_PENDING: Final[str] = OrderStatus.PENDING.value
