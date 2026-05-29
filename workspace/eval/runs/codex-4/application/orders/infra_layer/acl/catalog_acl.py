from django.db import IntegrityError
from django.db.models import F

from catalog.models import Product

from application.orders.domain_layer.order.port.product_inventory_port import (
    InventoryConflict,
    ProductInventoryPort,
    ProductInventorySnapshot,
    ProductNotFound,
)
from application.orders.domain_layer.order.value_object.quantity import Quantity


class DjangoProductInventoryPort(ProductInventoryPort):
    def load_snapshot(self, product_id: int) -> ProductInventorySnapshot:
        try:
            product = Product.objects.select_for_update().get(pk=product_id)
        except Product.DoesNotExist as exc:
            raise ProductNotFound("product not found") from exc
        return ProductInventorySnapshot(
            product_id=product.id,
            available_stock=product.stock,
            version=product.version,
        )

    def decrement_stock(
        self,
        snapshot: ProductInventorySnapshot,
        quantity: Quantity,
    ) -> None:
        try:
            updated_count = (
                Product.objects.filter(
                    pk=snapshot.product_id,
                    version=snapshot.version,
                ).update(
                    stock=F("stock") - quantity.value,
                    version=F("version") + 1,
                )
            )
        except IntegrityError as exc:
            raise InventoryConflict("inventory constraint conflict") from exc
        if updated_count != 1:
            raise InventoryConflict("inventory version conflict")
