from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from application.orders.domain_layer.order.exception import InsufficientStock
from application.orders.domain_layer.order.port.product_inventory_port import (
    ProductInventorySnapshot,
)
from application.orders.domain_layer.order.value_object.quantity import Quantity


@dataclass(frozen=True)
class Order:
    product_id: int
    quantity: int
    status: str = "created"
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    @classmethod
    def create(
        cls,
        *,
        product_id: int,
        quantity: Quantity,
        inventory_snapshot: ProductInventorySnapshot,
    ) -> "Order":
        if quantity.value > inventory_snapshot.available_stock:
            raise InsufficientStock(
                available_stock=inventory_snapshot.available_stock,
                requested_quantity=quantity.value,
            )
        return cls(product_id=product_id, quantity=quantity.value)
