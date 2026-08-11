from django.db import models


class InvoiceModel(models.Model):
    class Meta:
        db_table = "billing_invoice"
