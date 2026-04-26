from django.contrib import admin

from products.models import Category, Product, Seller


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "is_verified", "created_at"]
    list_filter = ["is_verified"]
    search_fields = ["name", "email"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "price",
        "category",
        "stock",
        "discount_rate",
        "rating",
        "seller",
        "is_active",
    ]
    list_filter = ["is_active", "category", "seller"]
    search_fields = ["name", "description"]
