from django.contrib import admin

from .models import Inventory


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = [
        "product",
        "warehouse",
        "quantity_received",
        "quantity_shipped",
        "available_stock",
        "last_received_at",
    ]
    list_filter = ["warehouse"]
    search_fields = [
        "product__name",
        "warehouse__name",
    ]
    list_select_related = ["product", "warehouse"]
    readonly_fields = ["available_stock"]
