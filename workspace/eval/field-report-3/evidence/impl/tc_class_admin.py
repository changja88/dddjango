from __future__ import annotations
from typing import TYPE_CHECKING
from django.contrib import admin
from application.fortune_character.driven_layer.django_fortune_character.models.character_model import CharacterModel

if TYPE_CHECKING:
    class _CharacterModelAdmin(admin.ModelAdmin[CharacterModel]):
        pass
else:
    _CharacterModelAdmin: type[admin.ModelAdmin] = admin.ModelAdmin


class CharacterPanel(_CharacterModelAdmin):
    list_display = ("id",)
