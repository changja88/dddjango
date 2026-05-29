from django.db import models


class ProductModel(models.Model):
    name = models.CharField(max_length=200)
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        app_label = "django_inventory"
