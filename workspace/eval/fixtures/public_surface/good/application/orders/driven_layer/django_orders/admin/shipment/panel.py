from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib import admin

from application.orders.driven_layer.django_orders.models.account_user_model import AccountUser

if TYPE_CHECKING:  # TYPE_CHECKING 분기 안 중간 ClassDef 도 같은 별칭이다 — 런타임 분기는 맨 클래스
    class _ShipmentAdminBase(admin.ModelAdmin[AccountUser]):
        pass
else:
    _ShipmentAdminBase: type[admin.ModelAdmin] = admin.ModelAdmin


class ShipmentPanel(_ShipmentAdminBase):
    list_display = ("email",)
