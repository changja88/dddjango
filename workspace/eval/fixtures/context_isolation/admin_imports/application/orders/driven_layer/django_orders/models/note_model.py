from django.db import models

from ....domain_layer.order.value_object.money import Money


class NoteModel(models.Model):
    body: models.TextField = models.TextField()
