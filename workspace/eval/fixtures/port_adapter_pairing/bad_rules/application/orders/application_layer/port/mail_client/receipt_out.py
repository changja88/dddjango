from __future__ import annotations

from dataclasses import dataclass

import application.orders.domain_layer.order.order as order_root
from application.orders.domain_layer.order.entity.order_line import OrderLine
from application.orders.domain_layer.order.value_object import Order
from application.orders.domain_layer.shared_value_object import Money
from application.orders.domain_layer.value_object.order_code import OrderCode
from application.orders.domain_layer.domain_service.value_object.quote import Quote
from application.orders.domain_layer.order.entity.value_object.line_code import LineCode

from .... import domain_layer


@dataclass(frozen=True)
class ReceiptOut:
    order: order_root.Order
    line: OrderLine
    head: Order
    total: Money
    code: OrderCode
    quote: Quote
    line_code: LineCode
    placed: domain_layer.order.order.Order
