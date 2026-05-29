from django.db.models import F

from application.inventory.infra_layer.django_inventory.models.product_model import (
    ProductModel,
)


class ProductRepository:
    """Persistence for products."""

    def deduct_stock(self, product_id: int, quantity: int) -> bool:
        """Decrement stock for the product in a single atomic statement.

        Returns ``True`` when the row was updated, ``False`` otherwise.
        """
        updated = ProductModel.objects.filter(
            id=product_id, stock__gte=quantity
        ).update(stock=F("stock") - quantity)
        return updated == 1
