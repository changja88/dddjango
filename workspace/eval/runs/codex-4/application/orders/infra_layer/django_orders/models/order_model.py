from django.db import models

from catalog.models import Product


class OrderModel(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=32, default="created")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(quantity__gt=0),
                name="orders_order_quantity_positive",
            ),
            models.CheckConstraint(
                check=models.Q(status__in=["created"]),
                name="orders_order_status_created",
            ),
        ]
