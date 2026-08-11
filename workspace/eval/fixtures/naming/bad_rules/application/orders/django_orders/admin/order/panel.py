from __future__ import annotations

from django.contrib.admin import ModelAdmin
from django.forms import ModelForm


class RefundForm(ModelForm):
    pass


class OrderPanel(ModelAdmin):
    def save_model(self, request, obj, form, change) -> None:
        for line in obj.lines.objects.all():
            line.archive()
