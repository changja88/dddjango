from django.urls import path

from application.catalog.presentation_layer.api.create_order.api_orders import (
    create_order,
)

urlpatterns = [
    path("orders/", create_order, name="catalog-create-order"),
]
