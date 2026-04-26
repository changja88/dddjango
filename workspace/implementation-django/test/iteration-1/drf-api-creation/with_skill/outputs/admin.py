from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["product_name", "quantity", "unit_price"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "total_amount", "status", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["user__username", "user__email"]
    readonly_fields = ["total_amount", "created_at", "updated_at"]
    inlines = [OrderItemInline]
