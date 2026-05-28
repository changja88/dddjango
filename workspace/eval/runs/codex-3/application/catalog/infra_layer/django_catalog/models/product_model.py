from django.db import models


class ProductModel(models.Model):
    name = models.CharField(max_length=200)
    price = models.PositiveIntegerField()
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "catalog_product"
        constraints = [
            models.CheckConstraint(
                check=models.Q(price__gte=0),
                name="catalog_product_price_gte_0",
            ),
            models.CheckConstraint(
                check=models.Q(stock__gte=0),
                name="catalog_product_stock_gte_0",
            ),
        ]
