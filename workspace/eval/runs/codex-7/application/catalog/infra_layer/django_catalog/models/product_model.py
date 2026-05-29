from django.db import models


class ProductModel(models.Model):
    name = models.CharField(max_length=200)
    price = models.PositiveIntegerField()
    stock = models.PositiveIntegerField(default=0)
    version = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "catalog_product"
        constraints = [
            models.CheckConstraint(
                check=models.Q(stock__gte=0),
                name="catalog_product_stock_nonnegative",
            ),
            models.CheckConstraint(
                check=models.Q(version__gte=0),
                name="catalog_product_version_nonnegative",
            ),
        ]

    def __str__(self) -> str:
        return self.name

