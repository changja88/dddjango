"""S-1 monkeypatch 전제의 «직접 표기» 시제품 — settings 에 django_stubs_ext.monkeypatch() 가 있을 때의 모양."""
from __future__ import annotations

from typing import Any, ClassVar

from django import forms
from django.contrib import admin
from django.forms import BaseInlineFormSet, ModelForm
from django.http import HttpRequest

from application.fortune_character.driven_layer.django_fortune_character.models.character_model import CharacterModel
from application.fortune_character.driven_layer.django_fortune_character.models.media_model import MediaModel


class MediaInlineForm(forms.ModelForm[MediaModel]):
    class Meta:
        model = MediaModel
        fields = ("media_kind", "file")


class MediaInlineFormSet(BaseInlineFormSet[MediaModel, CharacterModel]):
    def clean(self) -> None:
        super().clean()


class MediaInline(admin.TabularInline[MediaModel, CharacterModel]):
    model: type[MediaModel] = MediaModel
    form: type[MediaInlineForm] = MediaInlineForm
    formset: type[MediaInlineFormSet] = MediaInlineFormSet
    extra: int = 0


class ProbeCharacterAdmin(admin.ModelAdmin[CharacterModel]):
    inlines: ClassVar[list[type[admin.TabularInline[Any, CharacterModel]]]] = [MediaInline]

    def save_model(self, request: HttpRequest, obj: CharacterModel, form: ModelForm[CharacterModel], change: bool) -> None:
        super().save_model(request, obj, form, change)


class ProbeStacked(admin.StackedInline[MediaModel, CharacterModel]):
    model: type[MediaModel] = MediaModel
