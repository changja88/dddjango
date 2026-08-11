from django.db import models


class Order(models.Model):
    total = models.DecimalField(max_digits=12, decimal_places=2)
