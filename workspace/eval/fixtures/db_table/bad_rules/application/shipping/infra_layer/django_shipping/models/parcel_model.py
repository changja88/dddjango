from django.db import models


class Parcel(models.Model):
    weight = models.IntegerField()
