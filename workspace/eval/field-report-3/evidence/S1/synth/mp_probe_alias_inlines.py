"""보고자 정본 예시(L106~L158)의 inlines 주석을 «타입 있는 기저» 아래에서 mypy 로 검증."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, TypeAlias

from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin
from django.forms import BaseInlineFormSet, ModelForm
from django.http import HttpRequest

from application.fortune_character.driven_layer.django_fortune_character.models.character_model import CharacterModel
from application.fortune_character.driven_layer.django_fortune_character.models.media_model import MediaModel

if TYPE_CHECKING:
    _InlineBase: TypeAlias = admin.TabularInline[MediaModel, CharacterModel]  # noqa: UP040
    _ModelAdminBase: TypeAlias = admin.ModelAdmin[CharacterModel]  # noqa: UP040
else:
    _InlineBase: type[admin.TabularInline] = admin.TabularInline
    _ModelAdminBase: type[admin.ModelAdmin] = admin.ModelAdmin

type ParentInlineFormSet = BaseInlineFormSet[Any, CharacterModel, Any]


class MediaInline(_InlineBase):
    model: type[MediaModel] = MediaModel
    extra: int = 0


# (R) 보고자 L153 그대로
class AdminR(_ModelAdminBase):
    inlines: ClassVar[list[type[admin.TabularInline[Any, CharacterModel]]]] = [MediaInline]

    def save_related(self, request: HttpRequest, form: ModelForm[CharacterModel], formsets: list[ParentInlineFormSet], change: bool) -> None: ...


# (1) 스텁 선언과 같은 원소 타입
class Admin1(_ModelAdminBase):
    inlines: ClassVar[list[type[InlineModelAdmin[Any, Any]]]] = [MediaInline]


# (2) 주석 없이(첫 대입 타입 없음 — #493 과 충돌 여부는 별도)
class Admin2(_ModelAdminBase):
    inlines = [MediaInline]


# (3) tuple 로
class Admin3(_ModelAdminBase):
    inlines: ClassVar[tuple[type[InlineModelAdmin[Any, Any]], ...]] = (MediaInline,)


# (4) Sequence
from collections.abc import Sequence  # noqa: E402
class Admin4(_ModelAdminBase):
    inlines: ClassVar[Sequence[type[InlineModelAdmin[Any, Any]]]] = (MediaInline,)
