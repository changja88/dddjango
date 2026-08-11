from django.db import models
from application.orders.domain_layer.order.order import Order
from application.billing.driven_layer.django_billing.models.invoice_model import InvoiceModel


class OrderModel(models.Model):
    invoice = models.ForeignKey("billing.InvoiceModel", on_delete=models.PROTECT)
    payer = models.OneToOneField(InvoiceModel, on_delete=models.PROTECT)

    class Meta:
        db_table = "wrong_order"


class OrderLineModel(models.Model):
    order = models.ForeignKey("orders.OrderModel", on_delete=models.CASCADE)

    class Meta:
        db_table = "orders_order_line"
