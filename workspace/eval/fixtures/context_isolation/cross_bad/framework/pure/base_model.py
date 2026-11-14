from django.db import models


class TimestampedModel(models.Model):
    class Meta:
        abstract = True
