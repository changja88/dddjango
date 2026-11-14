from django.db import models

from application.orders.domain_layer.order.value_object.money import Money
import application.orders.domain_layer.order.value_object.money as money_mod

Amount = Money


class OrderModel(models.Model):
    total: models.IntegerField = models.IntegerField()
