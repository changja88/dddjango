from __future__ import annotations

import threading
from contextlib import nullcontext
from dataclasses import dataclass
from typing import ContextManager

from django.db import connection, transaction
from django.db.models import F

from catalog.exceptions import InsufficientStock, InvalidOrderQuantity, ProductNotFound
from catalog.models import Order, Product


_sqlite_order_write_lock = threading.Lock()


@dataclass(frozen=True)
class CreateOrderResult:
    order_id: int
    product_id: int
    quantity: int
    unit_price: int
    total_price: int
    remaining_stock: int


def create_order(*, product_id: int, quantity: int) -> CreateOrderResult:
    if quantity <= 0:
        raise InvalidOrderQuantity

    with _order_write_context(), transaction.atomic():
        updated_count = Product.objects.filter(
            id=product_id,
            stock__gte=quantity,
        ).update(stock=F("stock") - quantity)

        if updated_count == 0:
            if Product.objects.filter(id=product_id).exists():
                raise InsufficientStock
            raise ProductNotFound

        product = Product.objects.get(id=product_id)
        order = Order.for_product(product=product, quantity=quantity)
        order.save()

        return CreateOrderResult(
            order_id=order.id,
            product_id=product.id,
            quantity=order.quantity,
            unit_price=order.unit_price,
            total_price=order.total_price,
            remaining_stock=product.stock,
        )


def _order_write_context() -> ContextManager[object]:
    if connection.vendor == "sqlite":
        return _sqlite_order_write_lock

    return nullcontext()
