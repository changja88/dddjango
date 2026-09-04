from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias

from django.contrib import admin

from application.orders.driven_layer.django_orders.admin.order.form.line_form import OrderLineForm
from application.orders.driven_layer.django_orders.models.account_user_model import AccountUser

if TYPE_CHECKING:  # django-stubs 전용 — 런타임 클래스는 subscript 불가(houserules §4 · 별칭 기본)
    _OrderLineInlineBase: TypeAlias = admin.TabularInline[AccountUser, AccountUser]  # noqa: UP040
    _OrderAdminBase: TypeAlias = admin.ModelAdmin[AccountUser]  # noqa: UP040
else:
    _OrderLineInlineBase: type[admin.TabularInline] = admin.TabularInline
    _OrderAdminBase: type[admin.ModelAdmin] = admin.ModelAdmin


class OrderLineInline(_OrderLineInlineBase):
    model = AccountUser  # admin 선언 속성 — 스텁 ClassVar 가 타입을 소유(R-3154)
    form = OrderLineForm
    extra = 0


class OrderPanel(_OrderAdminBase):
    list_display = ("email", "display_name")
    readonly_fields = ("email",)
    inlines = [OrderLineInline]
