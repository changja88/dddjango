from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias

from django import forms

from application.orders.driven_layer.django_orders.models.account_user_model import AccountUser

if TYPE_CHECKING:  # ModelForm 기저는 django-stubs 제네릭 — 별칭으로 모델 타입 인자(houserules §4)
    _OrderLineFormBase: TypeAlias = forms.ModelForm[AccountUser]  # noqa: UP040
else:
    _OrderLineFormBase: type[forms.ModelForm] = forms.ModelForm


class OrderLineForm(_OrderLineFormBase):
    class Meta:
        model = AccountUser
        fields = ("email", "display_name")
