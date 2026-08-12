from django.db import models


class CustomerModel(models.Model):
    email = models.EmailField(unique=True)

    class Meta:
        db_table = "orders_customer"
