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

    def clean(self) -> dict[str, object]:  # ModelForm 도 스텁상 BaseForm.clean 오버라이드 — 별칭 기저 해소 뒤 `dict[str, object]` 반환은 #647 면제
        super().clean()
        return {"email": self.cleaned_data.get("email")}
