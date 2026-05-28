from django.db import models


class ProductModel(models.Model):
    name = models.CharField(max_length=200)
    price = models.PositiveIntegerField()
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "catalog_product"

