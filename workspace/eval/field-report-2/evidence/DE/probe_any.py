from typing import Any
from django import forms
from django.contrib import admin
from django.db import models
from django.http import HttpRequest


class Thing2(models.Model):
    name = models.CharField(max_length=10)

    def delete(self, using: Any = None, keep_parents: bool = False) -> tuple[int, dict[str, int]]:
        return super().delete(using=using, keep_parents=keep_parents)


class ThingForm2(forms.ModelForm[Thing2]):
    class Meta:
        model = Thing2
        fields = ("name",)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def clean(self) -> dict[str, Any]:
        return super().clean()


class ThingAdmin2(admin.ModelAdmin[Thing2]):
    def has_change_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        return True
