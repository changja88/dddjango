from django.db import models


class OrderStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PAID = "paid", "Paid"


class OrderModel(models.Model):
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default="pending",
    )

    class Meta:
        db_table = "orders_order"
