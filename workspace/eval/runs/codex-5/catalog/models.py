from django.db import models
from django.db.models import Q


class InsufficientStock(Exception):
    pass


class InvalidReservationQuantity(ValueError):
    pass


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.PositiveIntegerField()
    stock = models.PositiveIntegerField(default=0)
    version = models.PositiveIntegerField(default=0)

    def reserve(self, quantity: int) -> None:
        if quantity <= 0:
            raise InvalidReservationQuantity("Reservation quantity must be positive.")
        if self.stock < quantity:
            raise InsufficientStock("Product stock is lower than the requested quantity.")

        self.stock -= quantity

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(stock__gte=0),
                name="catalog_product_stock_non_negative",
            ),
        ]
