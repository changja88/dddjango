from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F
from django.db.models.functions import Now


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Inventory(TimeStampedModel):
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="inventories",
    )
    warehouse = models.ForeignKey(
        "warehouses.Warehouse",
        on_delete=models.CASCADE,
        related_name="inventories",
    )
    quantity_received = models.PositiveIntegerField(default=0)
    quantity_shipped = models.PositiveIntegerField(default=0)
    available_stock = models.GeneratedField(
        expression=F("quantity_received") - F("quantity_shipped"),
        output_field=models.IntegerField(),
        db_persist=True,
    )
    last_received_at = models.DateTimeField(db_default=Now())

    class Meta:
        verbose_name = "inventory"
        verbose_name_plural = "inventories"
        constraints = [
            models.UniqueConstraint(
                fields=["product", "warehouse"],
                name="unique_product_warehouse",
            ),
            models.CheckConstraint(
                condition=models.Q(quantity_received__gte=F("quantity_shipped")),
                name="available_stock_non_negative",
            ),
        ]

    def __str__(self):
        return f"{self.product} @ {self.warehouse}"

    def clean(self):
        if self.quantity_shipped > self.quantity_received:
            raise ValidationError(
                {
                    "quantity_shipped": (
                        "출고 수량은 입고 수량을 초과할 수 없습니다."
                    ),
                }
            )

    def receive(self, quantity):
        self.quantity_received = F("quantity_received") + quantity
        self.last_received_at = Now()
        self.save(update_fields=["quantity_received", "last_received_at", "updated_at"])
        self.refresh_from_db()

    def ship(self, quantity):
        self.refresh_from_db(fields=["quantity_received", "quantity_shipped"])
        new_shipped = self.quantity_shipped + quantity
        if new_shipped > self.quantity_received:
            raise ValidationError("가용 재고가 부족합니다.")
        self.quantity_shipped = new_shipped
        self.save(update_fields=["quantity_shipped", "updated_at"])
        self.refresh_from_db()
