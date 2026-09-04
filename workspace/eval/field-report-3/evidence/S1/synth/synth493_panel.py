from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias

from django import forms
from django.contrib import admin

from application.orders.driven_layer.django_orders.models.order_model import OrderModel

if TYPE_CHECKING:
    _AliasAdminBase: TypeAlias = admin.ModelAdmin[OrderModel]  # noqa: UP040
    _AliasFormBase: TypeAlias = forms.ModelForm[OrderModel]  # noqa: UP040
else:
    _AliasAdminBase: type[admin.ModelAdmin] = admin.ModelAdmin
    _AliasFormBase: type[forms.ModelForm] = forms.ModelForm


class BareAdmin(admin.ModelAdmin):
    list_display = ("id", "name")          # 선언적 면제 기대(#493 무발화)


class SubscriptAdmin(admin.ModelAdmin[OrderModel]):
    list_display = ("id", "name")          # 직접 subscript — 면제가 유지되나?


class AliasAdmin(_AliasAdminBase):
    list_display = ("id", "name")          # TYPE_CHECKING 별칭 — 면제가 유지되나?


class BareForm(forms.ModelForm):
    class Meta:
        model = OrderModel
        fields = ("name",)


class SubscriptForm(forms.ModelForm[OrderModel]):
    class Meta:
        model = OrderModel
        fields = ("name",)


class AliasForm(_AliasFormBase):
    class Meta:
        model = OrderModel
        fields = ("name",)
