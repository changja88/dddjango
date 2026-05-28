from django.db import models
from django.db.models import Q

from application.catalog.infra_layer.django_catalog.models.product_model import ProductModel


class OrderModel(models.Model):
    product = models.ForeignKey(ProductModel, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=Q(quantity__gte=1), name="catalog_order_quantity_gte_1"),
            models.CheckConstraint(check=Q(unit_price__gte=0), name="catalog_order_unit_price_gte_0"),
        ]

