from django import forms
from django.contrib import admin
from django.db import models
from django.http import HttpRequest


class Thing(models.Model):
    name = models.CharField(max_length=10)

    def delete(self, using: object = None, keep_parents: bool = False) -> tuple[int, dict[str, int]]:
        return super().delete(using=using, keep_parents=keep_parents)  # type: ignore[arg-type]


class ThingForm(forms.ModelForm[Thing]):
    class Meta:
        model = Thing
        fields = ("name",)

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)  # type: ignore[arg-type]

    def clean(self) -> dict[str, object]:
        cleaned: dict[str, object] = dict(super().clean())
        return cleaned


class ThingAdmin(admin.ModelAdmin[Thing]):
    def has_change_permission(self, request: HttpRequest, obj: object | None = None) -> bool:
        return True
