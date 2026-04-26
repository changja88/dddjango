from django.contrib import admin

from apps.products.models import Category, Product, Review, Seller


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "is_verified"]
    list_filter = ["is_verified"]
    search_fields = ["name", "email"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "stock", "discount_rate", "status", "category"]
    list_filter = ["status", "category"]
    search_fields = ["name"]
    raw_id_fields = ["seller"]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["product", "rating", "created_at"]
    list_filter = ["rating"]
    raw_id_fields = ["product"]
