from django.db import models

from catalog.exceptions import InsufficientStock, InvalidOrderQuantity


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.PositiveIntegerField()
    stock = models.PositiveIntegerField(default=0)

    def deduct_stock(self, quantity: int) -> int:
        if quantity <= 0:
            raise InvalidOrderQuantity
        if self.stock < quantity:
            raise InsufficientStock

        self.stock -= quantity
        return self.stock

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(stock__gte=0),
                name="catalog_product_stock_non_negative",
            ),
        ]


class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.PositiveIntegerField()
    total_price = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def for_product(cls, *, product: Product, quantity: int) -> "Order":
        if quantity <= 0:
            raise InvalidOrderQuantity

        return cls(
            product=product,
            quantity=quantity,
            unit_price=product.price,
            total_price=product.price * quantity,
        )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(quantity__gt=0),
                name="catalog_order_quantity_positive",
            ),
            models.CheckConstraint(
                check=models.Q(unit_price__gte=0),
                name="catalog_order_unit_price_non_negative",
            ),
            models.CheckConstraint(
                check=models.Q(total_price__gte=0),
                name="catalog_order_total_price_non_negative",
            ),
            models.CheckConstraint(
                check=models.Q(total_price=models.F("unit_price") * models.F("quantity")),
                name="catalog_order_total_price_matches_quantity",
            ),
        ]
