from __future__ import annotations
from django.contrib import admin
from django import forms
from application.fortune_character.driven_layer.django_fortune_character.models.character_model import CharacterModel as ParentModel
from application.fortune_character.driven_layer.django_fortune_character.models.media_model import MediaModel as ChildModel


class ChildForm(forms.ModelForm[ChildModel]):
    class Meta:
        model = ChildModel
        fields = ("mime",)


class ChildInline(admin.TabularInline[ChildModel, ParentModel]):
    model = ChildModel
    form = ChildForm
    extra = 0


class ParentAdmin(admin.ModelAdmin[ParentModel]):
    inlines = [ChildInline]
