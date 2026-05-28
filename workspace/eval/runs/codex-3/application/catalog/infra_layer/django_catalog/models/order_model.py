from django.db import models


class OrderModel(models.Model):
    product = models.ForeignKey(
        "catalog.ProductModel",
        on_delete=models.PROTECT,
        related_name="orders",
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "catalog_order"
        constraints = [
            models.CheckConstraint(
                check=models.Q(quantity__gt=0),
                name="catalog_order_quantity_gt_0",
            ),
            models.CheckConstraint(
                check=models.Q(unit_price__gte=0),
                name="catalog_order_unit_price_gte_0",
            ),
        ]
