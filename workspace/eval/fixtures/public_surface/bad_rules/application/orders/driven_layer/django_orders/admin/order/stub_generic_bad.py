from __future__ import annotations

from django import forms
from django.contrib import admin
from django.contrib.admin import ModelAdmin

from application.orders.driven_layer.django_orders.admin.order._bases import _SharedAdminBase
from application.orders.driven_layer.django_orders.models.account_user_model import AccountUser


class BareNamePanel(ModelAdmin):  # ⓐ 맨몸(Name)
    list_display = ("email",)


class BareAttributeInline(admin.TabularInline):  # ⓐ 맨몸(Attribute)
    model = AccountUser


class MultiLineIgnorePanel(
    admin.ModelAdmin,  # type: ignore[type-arg]
):  # ⓑ 여러 줄 헤더 · ⓐ+ⓑ 는 클래스당 1건
    list_display = ("email",)


class AttributeLineIgnorePanel(admin.ModelAdmin[AccountUser]):
    inlines = [BareAttributeInline]  # type: ignore[type-arg]


class SharedAliasPanel(_SharedAdminBase):  # type: ignore[type-arg]
    list_display = ("email",)


class BareForm(forms.ModelForm):  # ⓐ 맨몸 form
    class Meta:
        model = AccountUser
        fields = ("email",)
