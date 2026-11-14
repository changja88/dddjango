from django.db import models


class SuspensionNoteModel(models.Model):
    note = models.CharField(max_length=100)
