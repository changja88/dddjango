from django.urls import path

from catalog.api import reserve_product


urlpatterns = [
    path("products/<int:product_id>/reservations", reserve_product, name="product-reservations"),
]
