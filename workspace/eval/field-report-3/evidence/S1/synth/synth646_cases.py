from __future__ import annotations

import typing
from typing import TYPE_CHECKING, TypeAlias

import django.forms as f
from django import forms
from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin
from django.forms import ModelForm as MF
from parler.admin import TranslatableAdmin
from parler.forms import TranslatableModelForm

from application.orders.driven_layer.django_orders.admin.edge.shared_base import ImportedAliasBase
from application.orders.driven_layer.django_orders.models.order_model import OrderModel

if TYPE_CHECKING:
    _TcAlias: TypeAlias = admin.ModelAdmin[OrderModel]  # noqa: UP040
    class _TcClass(admin.TabularInline[OrderModel, OrderModel]):
        pass
else:
    _TcAlias: type[admin.ModelAdmin] = admin.ModelAdmin
    _TcClass: type[admin.TabularInline] = admin.TabularInline

if typing.TYPE_CHECKING:
    _TcAttrAlias: TypeAlias = forms.ModelForm[OrderModel]  # noqa: UP040
else:
    _TcAttrAlias = forms.ModelForm

_RtSubscriptAlias = admin.ModelAdmin[OrderModel]   # 런타임 TypeError 모양(monkeypatch 없으면) — 후보 기대
_RtBareAlias = admin.StackedInline                 # 모듈 수준 맨몸 별칭 → ⓐ 기대


class E01_Bare(admin.ModelAdmin):                  # ⓐ
    pass


class E02_AsImport(MF):                            # ⓐ (from … import ModelForm as MF)
    pass


class E03_ModuleAlias(f.ModelForm):                # ⓐ (import django.forms as f)
    pass


class E04_Subscript(admin.ModelAdmin[OrderModel]): # 통과
    pass


class E05_TcAlias(_TcAlias):                       # 통과(별칭)
    pass


class E06_TcClass(_TcClass):                       # 통과(TYPE_CHECKING 중간 클래스)
    pass


class E07_TcAttr(_TcAttrAlias):                    # 통과(typing.TYPE_CHECKING)
    pass


class E08_RtSubscript(_RtSubscriptAlias):          # 후보(cand-alias-subscript-runtime)
    pass


class E09_RtBare(_RtBareAlias):                    # ⓐ(alias-bare)
    pass


class E10_Parler(TranslatableAdmin):  # type: ignore[misc]   # 무발화 기대(기저 집합 밖)
    pass


class E11_ParlerForm(TranslatableModelForm):  # type: ignore[misc]
    pass


class E12_Mixin(TranslatableAdmin, admin.ModelAdmin[OrderModel]):  # type: ignore[misc]   # 통과(subscript) — misc 무관
    pass


class E13_Imported(ImportedAliasBase):             # 별칭 미해소(다른 모듈 import) → 무발화(사각)
    pass


class E14_MultiLineIgnore(                         # ⓑ (헤더 마지막 줄의 ignore)
    admin.ModelAdmin,
):  # type: ignore[type-arg]
    pass


class E15_BareIgnoreNoCode(admin.ModelAdmin):  # type: ignore
    pass


class E16_AttrIgnore(admin.ModelAdmin[OrderModel]):
    inlines: list[type[InlineModelAdmin]] = []  # type: ignore[type-arg]   # ⓑ′


class E17_InlineModelAdmin(InlineModelAdmin):      # ⓐ (options 경로)
    pass


def factory():
    class E18_Nested(forms.ModelForm):             # ⓐ (함수 안 — ast.walk)
        pass
    return E18_Nested


class E19_LocalShadow:  # 지역 클래스 이름이 ModelAdmin 인 경우
    pass


ModelAdmin = E19_LocalShadow  # noqa: F811


class E20_ShadowedName(ModelAdmin):                # 로컬 재정의 → import 바인딩 pop → 무발화 기대
    pass
