from __future__ import annotations

from dataclasses import dataclass

from application.orders.domain_layer.order.value_object.order_code import OrderCode
from application.orders.domain_layer.shared_value_object import money

from ....domain_layer.order.value_object.order_status import OrderStatus


@dataclass(frozen=True)
class ReceiptOut:
    code: OrderCode
    status: OrderStatus
    total: money.Money
