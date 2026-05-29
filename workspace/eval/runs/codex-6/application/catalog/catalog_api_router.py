from django.urls import path

from application.catalog.presentation_layer.api.reserve_product_stock.api_product_stock_reservations import (
    reserve_product_stock,
)

urlpatterns = [
    path(
        "products/<int:product_id>/stock-reservations",
        reserve_product_stock,
        name="reserve-product-stock",
    ),
]
