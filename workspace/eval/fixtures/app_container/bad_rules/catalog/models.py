from django.db import models


class CatalogItemModel(models.Model):
    name = models.CharField(max_length=100)
