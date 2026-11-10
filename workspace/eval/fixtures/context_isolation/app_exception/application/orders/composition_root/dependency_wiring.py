from __future__ import annotations

from application.orders.application_layer.order.place_order.place_order_use_case import PlaceOrderUseCase
from application.orders.application_layer.order.cancel_order.cancel_order_use_case import CancelOrderUseCase
from application.orders.application_layer.order.refund_order.refund_order_use_case import RefundOrderUseCase


def build_place_order_use_case() -> PlaceOrderUseCase:
    return PlaceOrderUseCase()


def build_cancel_order_use_case() -> CancelOrderUseCase:
    return CancelOrderUseCase()


def build_refund_order_use_case() -> RefundOrderUseCase:
    return RefundOrderUseCase()
