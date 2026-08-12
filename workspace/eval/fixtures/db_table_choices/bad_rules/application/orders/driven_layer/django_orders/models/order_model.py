from django.db import models


class OrderModel(models.Model):
    customer = models.ForeignKey("orders.CustomerModel", on_delete=models.PROTECT)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "orders_order"
