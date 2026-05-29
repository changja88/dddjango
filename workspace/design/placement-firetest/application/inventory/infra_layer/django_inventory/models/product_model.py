from django.db import models

from application.inventory.domain_layer.product.exceptions import InsufficientStock


class ProductModel(models.Model):
    name = models.CharField(max_length=200)
    available_stock = models.PositiveIntegerField(default=0)
    version = models.IntegerField(default=0)

    class Meta:
        app_label = "inventory"

    def reserve(self, quantity: int) -> None:
        if self.available_stock < quantity:
            raise InsufficientStock(
                f"available {self.available_stock}, requested {quantity}"
            )
        updated = ProductModel.objects.filter(
            pk=self.pk,
            version=self.version,
        ).update(
            available_stock=models.F("available_stock") - quantity,
            version=models.F("version") + 1,
        )
        if updated == 0:
            raise InsufficientStock("concurrent update conflict")
        self.available_stock -= quantity
        self.version += 1
