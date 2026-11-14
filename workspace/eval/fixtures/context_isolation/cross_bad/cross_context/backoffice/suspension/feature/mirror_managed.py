from django.db import models


class OrderMirror(models.Model):
    status: models.CharField = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = "orders_order"
