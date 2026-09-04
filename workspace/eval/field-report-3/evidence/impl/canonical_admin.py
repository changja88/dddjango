"""§18 정본 예시 검증 — ChildModel=MediaModel · ParentModel=CharacterModel (spring 실물)."""
from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, TypeAlias

from django import forms
from django.contrib import admin
from django.db.models import Model
from django.forms import BaseInlineFormSet, ModelForm
from django.http import HttpRequest

from application.fortune_character.driven_layer.django_fortune_character.models.character_model import CharacterModel as ParentModel
from application.fortune_character.driven_layer.django_fortune_character.models.media_model import MediaModel as ChildModel

if TYPE_CHECKING:  # django-stubs 전용 — 런타임 클래스는 subscript 불가
    _ChildFormBase: TypeAlias = forms.ModelForm[ChildModel]  # noqa: UP040
    _ChildFormSetBase: TypeAlias = BaseInlineFormSet[ChildModel, ParentModel]  # noqa: UP040 -- 셋째 인자(폼)는 기본값 ModelForm[ChildModel]
    _ChildInlineBase: TypeAlias = admin.TabularInline[ChildModel, ParentModel]  # noqa: UP040
    _ParentAdminBase: TypeAlias = admin.ModelAdmin[ParentModel]  # noqa: UP040
else:
    _ChildFormBase: type[forms.ModelForm] = forms.ModelForm
    _ChildFormSetBase: type[BaseInlineFormSet] = BaseInlineFormSet
    _ChildInlineBase: type[admin.TabularInline] = admin.TabularInline
    _ParentAdminBase: type[admin.ModelAdmin] = admin.ModelAdmin

type ParentInlineFormSet = BaseInlineFormSet[Model, ParentModel, ModelForm[Model]]


class ChildInlineForm(_ChildFormBase):
    class Meta:
        model = ChildModel
        fields = ("mime", "order")


class ChildInlineFormSet(_ChildFormSetBase):
    def clean(self) -> None: ...


class ChildInline(_ChildInlineBase):
    model = ChildModel
    form = ChildInlineForm
    formset = ChildInlineFormSet
    extra = 0


class ParentAdmin(_ParentAdminBase):
    readonly_fields = ("id",)
    inlines = [ChildInline]

    def save_model(self, request: HttpRequest, obj: ParentModel, form: ModelForm[ParentModel], change: bool) -> None: ...

    def save_related(self, request: HttpRequest, form: ModelForm[ParentModel], formsets: Sequence[ParentInlineFormSet], change: bool) -> None: ...
